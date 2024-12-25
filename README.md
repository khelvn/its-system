# Deploying ITS System on an Ubuntu Server

This guide provides step-by-step instructions for deploying and hosting the ITS System application on an Ubuntu server.

---

## Prerequisites
- An Ubuntu server (20.04 or later recommended).
- SSH access to the server.
- A domain name or server IP address.
- Basic knowledge of Linux terminal commands.

---

## Installation Steps

### 1. Update the System and Install Required Packages
Update your system packages and install Python, virtual environment tools, pip, and NGINX:
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip nginx
```

### 2. Set Up the Application
Navigate to the application directory and create a virtual environment:
```bash
cd its_system
python3 -m venv venv
source venv/bin/activate
```

Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Test the Application Locally
Run the application to ensure it's working before configuring Gunicorn:
```bash
python app.py -d
```

### 4. Install and Configure Gunicorn
Install Gunicorn and start the application in detached mode:
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 app:app -d
```

### 5. Create a Systemd Service
Create a Systemd service to manage the Gunicorn process. Edit the service file:
```bash
sudo nano /etc/systemd/system/its_system.service
```

Paste the following configuration, updating the placeholders (`your_user` and `/path/to/its_system`) with your actual values:
```ini
[Unit]
Description=Gunicorn instance to serve ITS app
After=network.target

[Service]
User=your_user
Group=www-data
WorkingDirectory=/path/to/its_system
Environment="PATH=/path/to/its_system/venv/bin"
ExecStart=/path/to/its_system/venv/bin/gunicorn --workers 3 --bind unix:its_system.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

Start and enable the service:
```bash
sudo systemctl start its_system
sudo systemctl enable its_system
```

### 6. Configure NGINX
Create an NGINX server block for your application:
```bash
sudo nano /etc/nginx/sites-available/its_system
```

Paste the following configuration, replacing `your_domain_or_ip` and `/path/to/its_system` with your details:
```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/its_system/its_system.sock;
    }

    location /static/ {
        alias /path/to/its_system/static/;
    }
}
```

Enable the NGINX configuration:
```bash
sudo ln -s /etc/nginx/sites-available/its_system /etc/nginx/sites-enabled
```

Test the configuration and restart NGINX:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

## Application Access
- Visit `http://your_domain_or_ip` in your browser to access the application.
- If you encounter issues, check the logs:
  - Gunicorn: `sudo journalctl -u its_system`
  - NGINX: `sudo tail -f /var/log/nginx/error.log`

---

## Notes
- Ensure the `static` folder contains the necessary static files for your app.
- Replace placeholders in configuration files with actual paths and credentials.
- Consider setting up a domain name and HTTPS using Let's Encrypt for secure access.

---

This concludes the deployment process.
