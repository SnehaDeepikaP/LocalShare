# Production Deployment & Operations Runbook — LocalShare

**Document Identifier:** DRB-LS-2026-V2.0  
**Target Environments:** Linux / Docker / Render / Heroku / AWS / VPS  
**WSGI Servers Supported:** Waitress 3.0.2 & Gunicorn 21+  

---

## 1. Hosting Environment Prerequisites

1. **Operating System:** Ubuntu 22.04 LTS / Debian 12 / Alpine Linux (or Windows Server 2022).
2. **Python Runtime:** Python 3.11, 3.12, or 3.13 (64-bit).
3. **Database:** SQLite 3 (with persistent volume mounted) or PostgreSQL 14+.
4. **Reverse Proxy:** Nginx or Caddy with TLS termination (Let's Encrypt SSL certificates).
5. **Memory & CPU:** Minimum 512 MB RAM, 1 vCPU; recommended 1 GB RAM, 2 vCPUs.

---

## 2. Environment Variables Configuration

Copy `.env.example` to `.env` on the host:
```bash
cp .env.example .env
```

Set the following variables:
```ini
# Flask Core
FLASK_CONFIG=production
FLASK_DEBUG=false

# Cryptographic Secret (Generate using: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=9f3b17d84a2c09e51f82b7405cde189a63b40d7e52a8190c4fb318d29a56e721

# Database Configuration:
# Option A: SQLite on persistent disk mount
DATABASE_URL=sqlite:////var/data/localshare/localshare.db

# Option B: Managed PostgreSQL
# DATABASE_URL=postgresql://localshare_user:StrongPassword@db.provider.internal:5432/localshare_prod

# Port & Host
HOST=0.0.0.0
PORT=5000

# Rate Limiting
LOGIN_RATE_LIMIT_ATTEMPTS=5
LOGIN_RATE_LIMIT_WINDOW_SECONDS=300
```

---

## 3. Step-by-Step Production Deployment

### 3.1 Bare Metal / Virtual Private Server (VPS)

1. **Clone repository and set permissions:**
   ```bash
   git clone <repository-url> /opt/localshare
   cd /opt/localshare
   ```
2. **Create virtual environment and install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. **Initialize database schema and default admin account:**
   ```bash
   flask init-db
   ```
   *(Creates tables and seeds default administrator `admin@localshare.dev` / `Admin@123`)*.
4. **Run automated smoke test suite:**
   ```bash
   python -m pytest
   ```
   *(Verify all 34 tests pass before starting public traffic)*.
5. **Start WSGI Server using Waitress or Gunicorn:**
   - *Using Waitress (Cross-Platform):*
     ```bash
     python -m waitress --listen=0.0.0.0:5000 wsgi:app
     ```
   - *Using Gunicorn (Linux/POSIX):*
     ```bash
     pip install gunicorn
     gunicorn --workers 3 --bind 0.0.0.0:5000 --access-logfile /var/log/localshare_access.log wsgi:app
     ```

### 3.2 Systemd Service Unit (`/etc/systemd/system/localshare.service`)

```ini
[Unit]
Description=LocalShare Community Mutual Aid Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/localshare
Environment="PATH=/opt/localshare/venv/bin"
EnvironmentFile=/opt/localshare/.env
ExecStart=/opt/localshare/venv/bin/python -m waitress --listen=127.0.0.1:5000 wsgi:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable localshare
sudo systemctl start localshare
sudo systemctl status localshare
```

### 3.3 Reverse Proxy & SSL (Nginx Configuration)

```nginx
server {
    listen 80;
    server_name localshare.yourdomain.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name localshare.yourdomain.org;

    ssl_certificate /etc/letsencrypt/live/localshare.yourdomain.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/localshare.yourdomain.org/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/localshare/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

---

## 4. Docker & Containerized Deployment

Using `docker-compose.yml`:
```bash
# Build and start container with background daemon
docker compose up -d --build

# Inspect logs
docker compose logs -f

# Verify container health
curl -f http://localhost:5000/health
```

---

## 5. Operations & Maintenance Procedures

### 5.1 Routine Backup Procedure
- **SQLite Database Backup:**
  ```bash
  mkdir -p /var/backups/localshare
  sqlite3 /opt/localshare/localshare.db ".backup '/var/backups/localshare/localshare_$(date +%Y%m%d_%H%M%S).db'"
  ```
- **Automated Backup Cron Job (`/etc/cron.daily/localshare_backup`):**
  ```bash
  #!/bin/bash
  BACKUP_DIR="/var/backups/localshare"
  mkdir -p "$BACKUP_DIR"
  sqlite3 /opt/localshare/localshare.db ".backup '$BACKUP_DIR/localshare_$(date +\%F).db'"
  # Keep only latest 14 days of backups
  find "$BACKUP_DIR" -type f -name "*.db" -mtime +14 -delete
  ```

### 5.2 Restoration Procedure
```bash
# 1. Stop service
sudo systemctl stop localshare

# 2. Restore file
cp /var/backups/localshare/localshare_2026-10-16.db /opt/localshare/localshare.db

# 3. Verify file integrity
sqlite3 /opt/localshare/localshare.db "PRAGMA integrity_check;"

# 4. Restart service
sudo systemctl start localshare
```

### 5.3 Health Check Monitoring & Alerting
- Monitoring agents (Uptime Kuma, Datadog, Prometheus) should ping `GET /health` every 60 seconds.
- An alert is fired if HTTP status code is non-200 or `database` field is `"disconnected"`.
