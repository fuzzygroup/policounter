# policounter

## About

Policounter is an open source crowd counting software designed to take crowd images from a camera, phone or drone and drive a website of images as well as build a data feed for algorithmic consumption.

## Data model explanation

An **Event** takes place in a **Location** and can have a series of **Observations** that include a crowd size **count**

![](https://github.com/fuzzygroup/policounter/blob/main/doc/policounter_datamodel.png)

## Crowd size estimation using lwcc

Policounter tracks several forms of observation, but also allows an observation to be the result of a machine prediciton.  To achieve this end the [LWCC: A LightWeight Crowd Counting library for Python](https://github.com/tersekmatija/lwcc) was employed.

Per the library [documentation](https://github.com/phwolf/lwcc/blob/master/README.md#Models):

LWCC currently offers 4 models (CSRNet, Bayesian crowd counting, DM-Count, SFANet) pretrained on [Shanghai A](https://ieeexplore.ieee.org/document/7780439), [Shanghai B](https://ieeexplore.ieee.org/document/7780439), and [UCF-QNRF](https://www.crcv.ucf.edu/data/ucf-qnrf/) datasets. The following table shows the model name and MAE / MSE result of the available pretrained models on the test sets.

|   Model name |      SHA       |      SHB      |      QNRF       |
| -----------: | :------------: | :-----------: | :-------------: |
|   **CSRNet** | 75.44 / 113.55 | 11.27 / 19.32 | *Not available* |
|      **Bay** | 66.92 / 112.07 | 8.27 / 13.56  | 90.43 / 161.41  |
| **DM-Count** | 61.39 / 98.56  | 7.68 / 12.66  | 88.97 / 154.11  |
|   **SFANet** |*Not available* | 7.05 / 12.18  | *Not available* |

Valid options for *model_name* are written in the first column and thus include: `CSRNet`, `Bay`, `DM-Count`, and `SFANet`.
Valid options for *model_weights* are written in the first row and thus include: `SHA`, `SHB`,  and `QNRF`.

**Note**: Not all *model_weights* are supported with all *model_names*. See the above table for possible combinations.


## requirements

- numpy>=1.14.0
- torch>=1.6
- gdown>=3.10.1
- torchvision
- pillow>=8.0
- django
    - psycopg[binary]

# Policounter Django Deployment Guide (Ubuntu + Gunicorn + Nginx)

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
DB_NAME=pcdb
DB_USER=pcdbu
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
CREATE DATABASE pcdb;
CREATE USER pcdbu WITH PASSWORD 'your-password';
ALTER ROLE pcdbu SET client_encoding TO 'utf8';
ALTER ROLE pcdbu SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE pcdb TO pcdbu;
```

Ensure:

```sql
GRANT ALL ON SCHEMA public TO pcdbu;
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

You now have a working, minimal, stable Django production deploy. 🎉

