package main

import (
	"admin_panel/middlewares"
	"admin_panel/routes"
	"admin_panel/services"
	"admin_panel/utils"
	"fmt"
	"net/http"
	"os"

	"github.com/gin-contrib/sessions"
	"github.com/gin-contrib/sessions/cookie"
	"github.com/gin-gonic/gin"
	log "github.com/sirupsen/logrus"
)

func main() {
	// Load environment variables
	err := utils.LoadEnv()
	if err != nil {
		log.Fatalf("Error loading .env file: %v", err)
	}

	// Initialize logging
	log.SetFormatter(&log.JSONFormatter{})
	log.SetOutput(gin.DefaultWriter)
	log.SetLevel(log.InfoLevel)

	// Initialize database
	err = services.InitializeDatabase()
	if err != nil {
		log.Fatalf("Failed to connect to the database: %v", err)
	}
	defer services.CloseDatabase()

	// Create the uploads directory
	err = os.MkdirAll("uploads", os.ModePerm)
	if err != nil {
		log.Fatalf("Failed to create uploads directory: %v", err)
	}

	// Set up Gin router
	r := gin.Default()

	// Set up session middleware
	store := cookie.NewStore([]byte("secret"))
	r.Use(sessions.Sessions("mysession", store))

	// Add middlewares
	r.Use(middlewares.LoggingMiddleware())

	// Static and template files
	r.Static("/static", "./static")
	r.LoadHTMLGlob("templates/*")

	// Routes
	r.GET("/", func(c *gin.Context) {
		c.Redirect(http.StatusFound, "/login")
	})
	r.GET("/login", routes.ShowLoginPage)
	r.POST("/login", routes.PerformLogin)
	r.GET("/dashboard", middlewares.AuthRequired(routes.ShowDashboard))
	r.POST("/upload", middlewares.AuthRequired(routes.HandleFileUpload))
	r.POST("/update-settings", middlewares.AuthRequired(routes.UpdateSettings))
	r.POST("/send-code", middlewares.AuthRequired(routes.SendCode))
	r.POST("/verify-code", middlewares.AuthRequired(routes.VerifyCode))
	r.POST("/start-adding-members", middlewares.AuthRequired(routes.StartAddingMembers))

	// Start the server
	port := "8080"
	if p := os.Getenv("PORT"); p != "" {
		port = p
	}
	log.Infof("Starting server on :%s", port)
	if err := r.Run(fmt.Sprintf(":%s", port)); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
