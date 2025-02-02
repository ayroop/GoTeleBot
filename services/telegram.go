package services

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
)

// GetUserDetails calls a Python script to get user details from phone numbers.
func GetUserDetails(phoneNumbers []string, outputJsonFile string) error {
	// Convert phone numbers to a format suitable for the Python script
	phoneNumbersFile := "phone_numbers.txt"
	err := os.WriteFile(phoneNumbersFile, []byte(strings.Join(phoneNumbers, "\n")), 0644)
	if err != nil {
		return fmt.Errorf("error writing phone numbers to file: %v", err)
	}

	// Ensure the temporary file is deleted after use
	defer os.Remove(phoneNumbersFile)

	cmd := exec.Command("venv/bin/python", "services/get_user_details.py", phoneNumbersFile, outputJsonFile)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("error getting user details: %v, output: %s", err, string(output))
	}
	fmt.Println(string(output))
	return nil
}

// AddMembersFromJson calls a Python script to add members to a Telegram group from a JSON file.
func AddMembersFromJson(jsonFile, targetGroup, apiToken string) error {
	cmd := exec.Command("venv/bin/python", "services/apify_adder.py", jsonFile)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("error adding members to channel: %v, output: %s", err, string(output))
	}
	fmt.Println(string(output))
	return nil
}
