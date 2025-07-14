# 🐙 Policounter

> *From estimating crowds to crafting the message—image work for the whole polly-verse.*

Policounter began life as a lightweight tool for estimating crowd sizes at protests using open-source computer vision. But like any good organizing effort, it's grown beyond its initial scope.

Now, it's evolving into a one-stop-shop for image handling in the **polly-verse**: a shared ecosystem for activists, organizers, and visually compelling data.

---

## 🚀 Functionality

### 🧍‍♂️ `policounter`
Estimates crowd sizes in protest images using [LWCC](https://github.com/tersekmatija/lwcc), a deep-learning-based crowd estimation framework.  
See [`policounter/README.md`](./policounter/README.md) for setup and usage.

---

### 🎨 `pollyvent`
Generates printable and shareable event flyers, complete with gradient backgrounds, logos, QR codes, and dynamically scaled text.  
See [`pollyvent/README.md`](./pollyvent/README.md) for full details and API examples.

---

## requirements

- numpy>=1.14.0
- torch>=1.6
- gdown>=3.10.1
- torchvision
- pillow>=8.0
- django
    - psycopg[binary]


# Policounter/pollyvent Django Deployment Guide (Ubuntu + Gunicorn + Nginx)

---

## Overview

This document outlines the production deployment process for the `policounter` Django project, covering initial setup, PostgreSQL, Gunicorn, Nginx, and environment configuration. It also includes a postmortem and cleanup plan for `requirements.txt`.

---

## 1. Provision Server

* OS: Ubuntu 22.04+
* Create a deploy user:

  ```bash
  adduser deploy
  usermod -aG sudo deploy
  ```
* Install dependencies:

  ```bash
  sudo apt update && sudo apt upgrade
  sudo apt install python3-venv python3-pip nginx postgresql postgresql-contrib
  ```

---

## 2. Clone Project & Setup Virtual Environment

```bash
cd ~
git clone https://your-repo-url ~/policounter
cd policounter
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Configure Environment Variables (No `export`, no quotes)

Create `.env` at the project root:

```
SECRET_KEY=your-new-secret-key
DB_NAME=<dbname>
DB_USER=<dbuser>
DB_PASSWORD=your-password
```

Permissions:

```bash
chmod 640 .env
chown deploy:www-data .env
```

---

## 4. PostgreSQL Setup

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE <dbname>;
CREATE USER <dbuser> WITH PASSWORD 'your-password';
ALTER ROLE <dbuser> SET client_encoding TO 'utf8';
ALTER ROLE <dbuser> SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE <dbname> TO <dbuser>;
```

Ensure:

```sql
GRANT ALL ON SCHEMA public TO <dbuser>;
```

---

## 5. Update `settings.py`

```python
import os

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS = ['your.server.ip', 'localhost', 'your.domain.com']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

---

## 6. Migrations and Collectstatic

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic
```

---

## 7. Gunicorn Systemd Service

File: `/etc/systemd/system/policounter.service`

```ini
[Unit]
Description=Gunicorn daemon for policounter Django project
After=network.target

[Service]
User=deploy
Group=www-data
WorkingDirectory=/home/deploy/policounter
EnvironmentFile=/home/deploy/policounter/.env
ExecStart=/home/deploy/policounter/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/deploy/policounter/policounter.sock \
          policounter.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable policounter
sudo systemctl start policounter
```

---

## 8. NGINX Configuration

File: `/etc/nginx/sites-available/policounter`

```nginx
server {
    listen 80;
    server_name your.domain.com your.server.ip;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/deploy/policounter/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/deploy/policounter/policounter.sock;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/policounter /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl reload nginx
```

---

## 9. Firewall and HTTPS

```bash
sudo ufw allow 'Nginx Full'
```

(Optional HTTPS):

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your.domain.com
```

---

## ✅ Deployment Complete

Visit: `http://your.server.ip/` or `http://your.domain.com/` to verify.

## 🤝 License & Attribution
policounter uses LWCC under the MIT license.

pollyvent builds on Pillow, qrcode, and other open libraries.

pollycounter is written under AGPL-3.0 license

All work is copyright (c) [fuzzygroup].
