package services

import "database/sql"

// Settings represents the application settings
type Settings struct {
	BatchSize             int            `json:"batch_size"`
	TargetGroup           string         `json:"target_group"`
	ApiToken              string         `json:"api_token"`
	ApiId                 int            `json:"api_id"`
	ApiHash               string         `json:"api_hash"`
	AuthorizedPhoneNumber string         `json:"authorized_phone_number"`
	PhonePrefix           string         `json:"phone_prefix"`
	AuthorizationState    sql.NullString `json:"authorization_state"`
}
