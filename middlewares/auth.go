package middlewares

import (
	"net/http"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
)

func AuthRequired(handler gin.HandlerFunc) gin.HandlerFunc {
	return func(c *gin.Context) {
		session := sessions.Default(c)
		user := session.Get("user")
		if user == nil {
			c.Redirect(http.StatusFound, "/login")
			c.Abort()
			return
		}
		handler(c)
	}
}
