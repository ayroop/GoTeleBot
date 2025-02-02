# 🤖 Telegram Bot Adder

![GitHub License](https://img.shields.io/badge/license-MIT-green.svg)
![GitHub Stars](https://img.shields.io/github/stars/your-repo.svg)
![GitHub Forks](https://img.shields.io/github/forks/your-repo.svg)

🚀 A Telegram bot adder application built with Go and Python. Manage and add members to Telegram groups or channels via a web interface.

---

## 📚 Features
👉 Add members to Telegram groups/channels  
👉 Web-based management interface  
👉 Secure authentication and logging  
👉 PostgreSQL database integration  
👉 Deployable on Ubuntu VPS  

---

## 🚀 Deployment on Ubuntu VPS (Best Practices)

### 1⃣ Update & Install Dependencies
```sh
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget build-essential python3 python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx
```

### 2⃣ Clone the Repository
```sh
git clone https://github.com/Ayrop/telegram-bot-adder.git
cd telegram-bot-adder
```

### 3⃣ Set Up Environment Variables
Create a `.env` file in the project root:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=admin_user
DB_PASSWORD=YOUR-STRONG-PASSWORD
DB_NAME=admin_panel
PORT=8080
```

### 4⃣ Set Up PostgreSQL Database
```sh
sudo systemctl start postgresql
sudo systemctl enable postgresql

sudo -i -u postgres
psql

CREATE DATABASE admin_panel;
CREATE USER admin_user WITH PASSWORD 'YOUR-STRONG-PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE admin_panel TO admin_user;
\q
exit
```

#### ✅ Create Required Tables
```sql
\c admin_panel;

CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

INSERT INTO admins (username, password_hash) 
VALUES ('admin', 'YOUR-HASHED-PASSWORD');

CREATE TABLE telegram_config (
    id SERIAL PRIMARY KEY,
    api_token TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    phone_prefix TEXT DEFAULT '+98',
    rate_limit_count INTEGER DEFAULT 50,
    rate_limit_seconds INTEGER DEFAULT 120,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_accounts (
    id SERIAL PRIMARY KEY,
    api_token TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    daily_limit INT NOT NULL,
    minute_limit INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_account_usage (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    added_count INTEGER NOT NULL DEFAULT 0,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES api_accounts(id)
);
```

### 5⃣ Install Go & Python Dependencies
```sh
# Install Go
wget https://go.dev/dl/go1.20.3.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.20.3.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

go version  # Verify installation

go mod tidy

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6⃣ Build and Run the Go Application
```sh
go build -o telegram_bot_adder
./telegram_bot_adder
```

### 7⃣ Set Up Nginx Reverse Proxy with HTTPS
```sh
sudo nano /etc/nginx/sites-available/telegram_bot_adder
```
Add the following:
```nginx
server {
    listen 80;
    server_name your_domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your_domain.com;

    ssl_certificate /etc/letsencrypt/live/your_domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your_domain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```
Enable and restart Nginx:
```sh
sudo ln -s /etc/nginx/sites-available/telegram_bot_adder /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### 8⃣ Secure with SSL (Certbot)
```sh
sudo certbot --nginx -d your_domain.com
```

### 9⃣ Create a Systemd Service for Auto-Restart
```sh
sudo nano /etc/systemd/system/telegram_bot_adder.service
```
Add the following:
```ini
[Unit]
Description=Telegram Bot Adder
After=network.target

[Service]
ExecStart=/path/to/telegram_bot_adder
WorkingDirectory=/path/to/your/project
Restart=always
EnvironmentFile=/path/to/your/project/.env

[Install]
WantedBy=multi-user.target
```
Enable and start the service:
```sh
sudo systemctl enable telegram_bot_adder
sudo systemctl start telegram_bot_adder
```

### 📊 Monitor and Maintain
Check logs:
```sh
sudo journalctl -u telegram_bot_adder -f
```
Restart if needed:
```sh
sudo systemctl restart telegram_bot_adder
```

---

## 📚 Documentation
📚 [Read Full Documentation](https://ayrop.com/docs/GoTeleBot)

---

## 🤝 Contributing
👥 Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md).

---

## ⚖️ License
📚 This project is developed and maintained by **Ayrop.com - Pooriya Khorasani** under the [MIT License](LICENSE).

---

## 🌟 Show Your Support
Give a ⭐ if you like this project!
