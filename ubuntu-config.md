# Ubuntu Deployment Guide (with Apache)

This guide walks you through deploying your FastAPI app on an Ubuntu VPS using Apache as a reverse proxy.

---

## 1. Prepare Your VPS

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3.11-venv python3-pip git apache2 -y
```

Enable Apache proxy modules:
```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo systemctl restart apache2
```

---

## 2. Clone Your Repo

```bash
git clone https://github.com/DarkoKuzmanovic/verbatim-ai.git
cd verbatim-ai
```

---

## 3. Set Up Python Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in your project root:
```
OPENROUTER_API_KEY=your_api_key_here
```
(Add any other required variables from `config.py`.)

---

## 5. Run FastAPI with Uvicorn or Gunicorn

For development:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
For production (recommended):
```bash
pip install gunicorn
source venv/bin/activate
nohup gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --workers 4 &
```

---

## 6. Apache Reverse Proxy Setup

Create a new Apache site config (e.g., `/etc/apache2/sites-available/verbatim-ai.conf`):

```
<VirtualHost *:80>
    ServerName your_domain_or_ip

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    # Static files
    Alias /static/ /path/to/verbatim-ai/static/
    <Directory /path/to/verbatim-ai/static/>
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/verbatim-ai-error.log
    CustomLog ${APACHE_LOG_DIR}/verbatim-ai-access.log combined
</VirtualHost>
```

Enable the site and reload Apache:
```bash
sudo a2ensite verbatim-ai.conf
sudo systemctl reload apache2
```

---

## 7. (Optional) systemd Service for Gunicorn

Create `/etc/systemd/system/verbatim-ai.service`:
```
[Unit]
Description=Verbatim AI FastAPI Service
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/verbatim-ai
ExecStart=/path/to/verbatim-ai/venv/bin/gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable verbatim-ai
sudo systemctl start verbatim-ai
```

---

## 8. Test Your Deployment

- Visit `http://your_domain_or_ip/` in your browser.
- Test `/health` and `/api/test` endpoints.
- Check static file serving at `/static/`.

---

## Notes
- For HTTPS, use `certbot` and `mod_ssl` to secure your site.
- Adjust paths and usernames as needed for your environment.
- For troubleshooting, check Apache logs in `/var/log/apache2/` and Gunicorn logs.

---

Happy deploying!
