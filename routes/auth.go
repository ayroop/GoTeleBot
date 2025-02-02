package routes

import (
	"admin_panel/services"
	"admin_panel/utils"
	"fmt"
	"net/http"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
)

// ShowLoginPage renders the login page
func ShowLoginPage(c *gin.Context) {
	// Check if user is already authenticated
	session := sessions.Default(c)
	if session.Get("user") != nil {
		c.Redirect(http.StatusFound, "/dashboard")
		return
	}
	c.HTML(http.StatusOK, "login.html", nil)
}

// PerformLogin handles the login form submission
func PerformLogin(c *gin.Context) {
	username := c.PostForm("username")
	password := c.PostForm("password")

	var passwordHash string
	err := services.DB.QueryRow("SELECT password_hash FROM admins WHERE username=$1", username).Scan(&passwordHash)
	if err != nil {
		fmt.Printf("Login attempt failed for user %s: %v\n", username, err)
		c.HTML(http.StatusUnauthorized, "login.html", gin.H{"error": "Invalid credentials"})
		return
	}

	if utils.CheckPasswordHash(password, passwordHash) {
		session := sessions.Default(c)
		session.Set("user", username)
		session.Save()
		fmt.Printf("Successful login for user: %s\n", username)
		c.Redirect(http.StatusFound, "/dashboard")
	} else {
		fmt.Printf("Invalid password attempt for user: %s\n", username)
		c.HTML(http.StatusUnauthorized, "login.html", gin.H{"error": "Invalid credentials"})
	}
}
