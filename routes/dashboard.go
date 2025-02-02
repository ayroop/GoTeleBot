package routes

import (
	"database/sql"
	"fmt"
	"net/http"
	"os/exec"
	"strconv"

	"admin_panel/services"

	"github.com/gin-gonic/gin"
)

// ShowDashboard renders the dashboard page
func ShowDashboard(c *gin.Context) {
	settings, err := services.GetSettings()
	if err != nil {
		c.String(http.StatusInternalServerError, fmt.Sprintf("Error getting settings: %v", err))
		return
	}
	c.HTML(http.StatusOK, "dashboard.html", gin.H{
		"settings": settings,
	})
}

// UpdateSettings handles the settings update form submission
func UpdateSettings(c *gin.Context) {
	batchSize, err := strconv.Atoi(c.PostForm("batchSize"))
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid batch size")
		return
	}
	apiId, err := strconv.Atoi(c.PostForm("apiId"))
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid API ID")
		return
	}
	settings := services.Settings{
		BatchSize:             batchSize,
		TargetGroup:           c.PostForm("targetGroup"),
		ApiToken:              c.PostForm("apiToken"),
		ApiId:                 apiId,
		ApiHash:               c.PostForm("apiHash"),
		AuthorizedPhoneNumber: c.PostForm("authorizedPhoneNumber"),
		PhonePrefix:           c.PostForm("phonePrefix"),
		AuthorizationState:    sql.NullString{String: c.PostForm("authorizationState"), Valid: true},
	}
	err = services.UpdateSettings(settings)
	if err != nil {
		c.String(http.StatusInternalServerError, fmt.Sprintf("Error updating settings: %v", err))
		return
	}
	c.String(http.StatusOK, "Settings updated successfully")
}

// SendCode handles sending the authorization code
func SendCode(c *gin.Context) {
	apiId := c.PostForm("apiId")
	apiHash := c.PostForm("apiHash")
	phoneNumber := c.PostForm("authorizedPhoneNumber")

	cmd := exec.Command("venv/bin/python", "services/authorize_phone.py", apiId, apiHash, phoneNumber, "send_code")
	output, err := cmd.CombinedOutput()
	if err != nil {
		c.String(http.StatusInternalServerError, fmt.Sprintf("Error sending code: %v, output: %s", err, string(output)))
		return
	}
	c.String(http.StatusOK, string(output))
}

// VerifyCode handles verifying the authorization code
func VerifyCode(c *gin.Context) {
	apiId := c.PostForm("apiId")
	apiHash := c.PostForm("apiHash")
	phoneNumber := c.PostForm("authorizedPhoneNumber")
	code := c.PostForm("code")

	cmd := exec.Command("venv/bin/python", "services/authorize_phone.py", apiId, apiHash, phoneNumber, "verify_code", code)
	output, err := cmd.CombinedOutput()
	if err != nil {
		c.String(http.StatusInternalServerError, fmt.Sprintf("Error verifying code: %v, output: %s", err, string(output)))
		return
	}
	c.String(http.StatusOK, string(output))
}

// StartAddingMembers handles starting the process of adding members
func StartAddingMembers(c *gin.Context) {
	cmd := exec.Command("venv/bin/python", "services/add_members.py")
	output, err := cmd.CombinedOutput()
	if err != nil {
		c.String(http.StatusInternalServerError, fmt.Sprintf("Error adding members: %v, output: %s", err, string(output)))
		return
	}
	c.String(http.StatusOK, "Members added successfully")
}
