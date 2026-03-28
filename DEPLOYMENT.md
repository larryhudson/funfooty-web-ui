# Deploying Fun Footy on a VPS

This guide uses **Caddy** (reverse proxy with automatic HTTPS) and **Gunicorn** (Python WSGI server).

## Prerequisites

- A VPS (e.g. DigitalOcean, Hetzner, Linode) running Ubuntu/Debian
- A domain name with DNS A record pointing to the VPS IP
- SSH access to the server

## 1. Install system dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv caddy
```

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Deploy the app

Clone the repo and install dependencies:

```bash
cd /opt
sudo git clone <your-repo-url> funfooty
sudo chown -R $USER:$USER funfooty
cd funfooty/web-ui
uv sync
```

Test that it runs:

```bash
uv run gunicorn app:app --bind 127.0.0.1:8000
```

## 3. Set up the systemd service

Create `/etc/systemd/system/funfooty.service`:

```ini
[Unit]
Description=Fun Footy web app
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/funfooty/web-ui
ExecStart=/opt/funfooty/web-ui/.venv/bin/gunicorn app:app --bind 127.0.0.1:8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo chown -R www-data:www-data /opt/funfooty
sudo systemctl daemon-reload
sudo systemctl enable funfooty
sudo systemctl start funfooty
sudo systemctl status funfooty
```

## 4. Configure Caddy

Edit `/etc/caddy/Caddyfile`:

```
your-domain.com {
    reverse_proxy 127.0.0.1:8000
}
```

Replace `your-domain.com` with your actual domain.

Restart Caddy:

```bash
sudo systemctl restart caddy
```

Caddy will automatically provision a Let's Encrypt TLS certificate. This can take a minute or two the first time.

## 5. Verify

Visit `https://your-domain.com` in your browser. You should see the Fun Footy form.

## Updating

To deploy new changes:

```bash
cd /opt/funfooty
sudo -u www-data git pull
cd web-ui
sudo -u www-data uv sync
sudo systemctl restart funfooty
```

## Troubleshooting

Check app logs:

```bash
sudo journalctl -u funfooty -f
```

Check Caddy logs:

```bash
sudo journalctl -u caddy -f
```

If Caddy fails to get a certificate, make sure:
- Your domain's DNS A record points to the VPS IP
- Ports 80 and 443 are open in your firewall
