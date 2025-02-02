package routes

import (
	"admin_panel/services"
	"fmt"
	"log"
	"net/http"
	"path"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/tealeg/xlsx"
)

// HandleFileUpload handles the file upload form submission
func HandleFileUpload(c *gin.Context) {
	file, err := c.FormFile("phonefile")
	if err != nil {
		log.Printf("File upload error: %v", err)
		c.String(http.StatusBadRequest, fmt.Sprintf("File upload error: %v", err))
		return
	}

	filePath := path.Join("uploads", file.Filename)
	if err := c.SaveUploadedFile(file, filePath); err != nil {
		log.Printf("Could not save file: %v", err)
		c.String(http.StatusInternalServerError, fmt.Sprintf("Could not save file: %v", err))
		return
	}

	// Get settings from the database
	settings, err := services.GetSettings()
	if err != nil {
		log.Printf("Error getting settings: %v", err)
		c.String(http.StatusInternalServerError, fmt.Sprintf("Error getting settings: %v", err))
		return
	}

	// Convert phone numbers to international format and generate JSON data
	jsonFilePath := path.Join("uploads", "members.json")
	err = processFileAndGenerateJson(filePath, jsonFilePath, settings["PhonePrefix"])
	if err != nil {
		log.Printf("Error processing file: %v", err)
		c.String(http.StatusInternalServerError, fmt.Sprintf("Error processing file: %v", err))
		return
	}

	// Add members from JSON
	err = services.AddMembersFromJson(jsonFilePath, settings["TargetGroup"], settings["ApiToken"])
	if err != nil {
		log.Printf("Error adding members: %v", err)
		c.String(http.StatusInternalServerError, fmt.Sprintf("Error adding members: %v", err))
		return
	}

	c.String(http.StatusOK, "File uploaded and processed successfully")
}

func processFileAndGenerateJson(filePath, jsonFilePath, phonePrefix string) error {
	xlFile, err := xlsx.OpenFile(filePath)
	if err != nil {
		return fmt.Errorf("error opening file: %w", err)
	}

	var phoneNumbers []string
	for _, sheet := range xlFile.Sheets {
		for _, row := range sheet.Rows {
			for _, cell := range row.Cells {
				phone := cell.String()
				if strings.HasPrefix(phone, "0") {
					phone = phonePrefix + phone[1:]
					cell.SetString(phone)
				}
				phoneNumbers = append(phoneNumbers, phone)
			}
		}
	}

	// Save the updated file
	if err := xlFile.Save(filePath); err != nil {
		return fmt.Errorf("error saving file: %w", err)
	}

	// Process phone numbers in batches
	settings, err := services.GetSettings()
	if err != nil {
		return fmt.Errorf("error getting settings: %w", err)
	}
	batchSize, err := strconv.Atoi(settings["BatchSize"])
	if err != nil {
		return fmt.Errorf("invalid batch size: %w", err)
	}

	for i := 0; i < len(phoneNumbers); i += batchSize {
		end := i + batchSize
		if end > len(phoneNumbers) {
			end = len(phoneNumbers)
		}

		// Generate JSON data for the batch
		batch := phoneNumbers[i:end]
		batchJsonFilePath := fmt.Sprintf("%s_batch_%d.json", jsonFilePath, i/batchSize)
		err = services.GetUserDetails(batch, batchJsonFilePath)
		if err != nil {
			return fmt.Errorf("error generating JSON for batch %d: %w", i/batchSize, err)
		}

		// Call the Apify actor for the batch
		err = services.AddMembersFromJson(batchJsonFilePath, settings["TargetGroup"], settings["ApiToken"])
		if err != nil {
			return fmt.Errorf("error adding members for batch %d: %w", i/batchSize, err)
		}

		// Wait for a short period to avoid rate limits
		time.Sleep(1 * time.Minute)
	}

	return nil
}
