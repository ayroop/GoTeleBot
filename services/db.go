package services

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	_ "github.com/lib/pq"
)

var DB *sql.DB

// InitializeDatabase initializes the database connection
func InitializeDatabase() error {
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		os.Getenv("DB_HOST"),
		os.Getenv("DB_PORT"),
		os.Getenv("DB_USER"),
		os.Getenv("DB_PASSWORD"),
		os.Getenv("DB_NAME"))

	var err error
	DB, err = sql.Open("postgres", connStr)
	if err != nil {
		return fmt.Errorf("error opening database: %v", err)
	}

	err = DB.Ping()
	if err != nil {
		return fmt.Errorf("error connecting to the database: %v", err)
	}

	log.Println("Database connection established")
	return nil
}

// CloseDatabase closes the database connection
func CloseDatabase() {
	if DB != nil {
		err := DB.Close()
		if err != nil {
			log.Printf("Error closing database: %v", err)
		} else {
			log.Println("Database connection closed")
		}
	}
}

// GetSettings retrieves settings from the database
func GetSettings() (map[string]string, error) {
	settings := make(map[string]string)
	row := DB.QueryRow("SELECT batch_size, target_group, api_token, api_id, api_hash, authorized_phone_number, phone_prefix, authorization_state FROM settings WHERE id = 1")

	var batchSize int
	var targetGroup, apiToken, apiHash, authorizedPhoneNumber, phonePrefix, authorizationState string
	var apiId int

	err := row.Scan(&batchSize, &targetGroup, &apiToken, &apiId, &apiHash, &authorizedPhoneNumber, &phonePrefix, &authorizationState)
	if err != nil {
		return nil, fmt.Errorf("error querying settings: %v", err)
	}

	settings["BatchSize"] = fmt.Sprintf("%d", batchSize)
	settings["TargetGroup"] = targetGroup
	settings["ApiToken"] = apiToken
	settings["ApiId"] = fmt.Sprintf("%d", apiId)
	settings["ApiHash"] = apiHash
	settings["AuthorizedPhoneNumber"] = authorizedPhoneNumber
	settings["PhonePrefix"] = phonePrefix
	settings["AuthorizationState"] = authorizationState

	return settings, nil
}

// UpdateSettings updates settings in the database
func UpdateSettings(settings Settings) error {
	tx, err := DB.Begin()
	if err != nil {
		return fmt.Errorf("error beginning transaction: %v", err)
	}

	_, err = tx.Exec("UPDATE settings SET batch_size=$1, target_group=$2, api_token=$3, api_id=$4, api_hash=$5, authorized_phone_number=$6, phone_prefix=$7, authorization_state=$8 WHERE id=1",
		settings.BatchSize, settings.TargetGroup, settings.ApiToken, settings.ApiId, settings.ApiHash, settings.AuthorizedPhoneNumber, settings.PhonePrefix, settings.AuthorizationState)
	if err != nil {
		tx.Rollback()
		return fmt.Errorf("error updating settings: %v", err)
	}

	err = tx.Commit()
	if err != nil {
		return fmt.Errorf("error committing transaction: %v", err)
	}

	return nil
}
