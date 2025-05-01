# policounter

## About

Policounter is an open source crowd counting software designed to take crowd images from a camera, phone or drone and drive a website of images as well as build a data feed for algorithmic consumption.

## Data model explanation

An *Event* can have a series of *Observations* that include a crowd size *count*

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


## Policounter Deployment Instructions

### Prerequisites

Before deploying Policounter, ensure you have the following prerequisites installed:

* Python 3.8+
* pip (Python package manager)
* PostgreSQL database
* Git
* uWSGI and uWSGI Python3 plugin
* Nginx

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/fuzzygroup/policounter.git
cd policounter
```

#### 2. Setup a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install psycopg[binary]
pip install django-bootstrap5
```

#### 4. Configure Database
```bash
createdb pcdb --owner=pcdbu;

# Configure database settings in settings.py or .env file
# Example .env configuration:
# DB_NAME=pcdb
# DB_USER=pcdbu
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432
```

#### 5. Create and run migrations
```bash
python3 manage.py makemigrations    #in my env python3 is linked to the virtual env interpreter
python3 manage.py migrate
```

#### 6. Seed Database
```bash
python3 seeding/seed.py
python3 manage.py loaddata fixtures/data.json
```

#### 7. Create django admin panel username
```bash
python3 manage.py createsuperuser
```

#### 8. Run server
```bash
python3 manage.py runserver
```

### Production Deployment

For production deployment, consider the following additional steps:

### Using uWSGI and Nginx

#### 1. configure uwsgi

```bash
vim /etc/uwsgi/apps-available/yourdomain.com.uwsgi.ini
```

```ini
[uwsgi]
# Basic configuration
plugins = python3
master = true
protocol = uwsgi
socket = 127.0.0.1:8090

# Application configuration
chdir = /path/to/policounter
module = policounter.wsgi:application
home = /path/to/policounter/venv

# Worker configuration
workers = 4
enable-threads = true

# Performance settings
buffer-size = 8192
reload-on-rss = 250
close-on-exec = true

# Permissions
umask = 0022
uid = your_user
gid = your_group
chmod-socket = 660

# Error handling
ignore-sigpipe = true
ignore-write-errors = true
disable-write-exception = true

# Logging
logto = /var/log/uwsgi/app/policounter.log
log-date = true

# Cleanup
vacuum = true
die-on-term = true
```

#### 3. Enable the uWSGI Configuration

```bash
sudo ln -s /etc/uwsgi/apps-enabled/policounter.indiana50501.org.uwsgi.ini /etc/uwsgi/apps-available/policounter.indiana50501.org.uwsgi.ini
```

#### 4. Configure Nginx

Create an Nginz server block Configuration

```bash
sudo vim /etc/nginx/sites-available/policounter
```

Add the following configuration:

```nginx
vhost:

server {
  listen 80;
  listen [::]:80;
  listen 443 ssl http2;
  listen [::]:443 ssl http2;
  {{ssl_certificate_key}}
  {{ssl_certificate}}
  server_name policounter.indiana50501.org;
  {{root}}

  {{nginx_access_log}}
  {{nginx_error_log}}

  if ($scheme != "https") {
    rewrite ^ https://$host$uri permanent;
  }

  location ~ /.well-known {
    auth_basic off;
    allow all;
  }

  {{settings}}

  index index.html;

  location / {
    include uwsgi_params;
    uwsgi_read_timeout 3600;
    #uwsgi_pass unix:///run/uwsgi/app/weblate/socket;
    uwsgi_pass 127.0.0.1:{{app_port}};
  }

  location /static/ {
    alias /home/indiana50501-policounter/htdocs/policounter.indiana50501.org/static/;
  }

  location /media/ {
    alias /home/indiana50501-policounter/htdocs/policounter.indiana50501.org/media/;
  }


  #location ~* ^.+\.(css|js|jpg|jpeg|gif|png|ico|gz|svg|svgz|ttf|otf|woff|woff2|eot|mp4|ogg|ogv|webm|webp|zip|swf)$ {
  #  add_header Access-Control-Allow-Origin "*";
  #  expires max;
  #  access_log on;
  #}

  if (-f $request_filename) {
    break;
  }
}
```

#### 5. Enable the Nginx Configuration

```bash
sudo ln -s /etc/nginx/sites-available/policounter /etc/nginx/sites-enabled/
```


#### 6. Create Static and Media Directories

```bash
python3 manage.py collectstatic
mkdir -p media
chmod 755 static media
```

#### 7. Set proper permissions

```bash
sudo chown -R your_user:your_group /path/to/policounter
```

#### 8. Restart services

```bash
sudo systemctl restart uwsgi
sudo systemctl restart nginx
```

### Regular Maintenance

Back up the database regularly
Update the application and dependencies
Monitor server logs for errors

### Troubleshooting
If you encounter issues during deployment, check:

Application logs: /var/log/uwsgi/app/policounter.log
Nginx error logs: /var/log/nginx/policounter_error.log
PostgreSQL logs
System resource usage

For specific error troubleshooting, refer to the project documentation or open an issue on GitHub.
