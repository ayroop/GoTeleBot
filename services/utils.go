package services

import (
	"log"
	"os"
)

// CreateUploadsDirectory creates the uploads directory if it doesn't exist
func CreateUploadsDirectory() {
	uploadsDir := "uploads"
	if _, err := os.Stat(uploadsDir); os.IsNotExist(err) {
		err := os.Mkdir(uploadsDir, os.ModePerm)
		if err != nil {
			log.Fatalf("Failed to create uploads directory: %v", err)
		}
		log.Println("Uploads directory created")
	} else {
		log.Println("Uploads directory already exists")
	}
}
