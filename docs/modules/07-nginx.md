# Nginx

## Overview

Nginx is the reverse proxy and web server in this observability stack. It handles incoming HTTP requests, serves static files, and forwards dynamic requests to the Django application.

## Description

Nginx provides:
- Reverse proxy for Django application
- Static file serving (CSS, JS, images)
- Media file serving (uploaded files)
- Load balancing (if needed)
- HTTP caching

In this stack, Nginx:
- Listens on port 80
- Serves static files directly
- Proxies dynamic requests to Django (port 9000)
- Handles media file requests

## Purpose in Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NGINX IN STACK                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   INCOMING REQUESTS                                                         │
│   ─────────────────                                                         │
│                                                                             │
│        ┌──────────┐                                                         │
│        │  User    │                                                         │
│        │Browser   │                                                         │
│        └────┬─────┘                                                         │
│             │ HTTP (port 80)                                                │
│             ▼                                                               │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │                        NGINX :80                                │       │
│   │                                                                 │       │
│   │   ┌────────────────────┐    ┌────────────────────────────┐      │       │
│   │   │   Static Files     │    │   Dynamic Requests         │      │       │
│   │   │   /static/         │    │   /  → proxy to Django     │      │       │
│   │   │   /media/          │    │   /admin/                  │      │       │
│   │   │   /site-static/    │    │   /api/                    │      │       │
│   │   └────────────────────┘    └────────────┬───────────-───┘      │       │
│   │                                          │                      │       │
│   └──────────────────────────────────────────┴───────────-──────────┘       │
│                                              │                              │
│                                              ▼                              │
│                                    ┌─────────────────────┐                  │
│                                    │      Django         │                  │
│                                    │      :9000          │                  │
│                                    └─────────────────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology

| Component | Technology | Version |
|-----------|------------|---------|
| Web Server | Nginx | Alpine |
| Reverse Proxy | Nginx | - |

## Docker Configuration

### docker-compose.yml

```yaml
# Nginx Reverse Proxy
obs-nginx:
  image: nginx:alpine                   # Nginx on Alpine Linux (small image)
  container_name: obs-nginx
  restart: unless-stopped
  ports:
    - "80:80"                           # HTTP port
  volumes:
    - ./../nginx/nginx.conf:/etc/nginx/nginx.conf:ro  # Config file (read-only)
    - static_volume:/app/staticfiles:ro               # Django static files
    - media_volume:/app/mediafiles:ro                 # User uploads
  depends_on:
    - obs-django                        # Wait for Django to start
  networks:
    - app_network                       # Can proxy to Django
```

### nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    include      /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream django {
        server obs-django:9000;
    }

    server {
        listen 80;
        server_name localhost;

        # Static files from Django collectstatic
        location /static/ {
            alias /app/static/;
        }

        # User-uploaded media files
        location /media/ {
            alias /app/mediafiles/;
        }

        # Direct static files (no collectstatic needed)
        location /site-static/ {
            alias /app/site_static/;
        }

        # All other requests → Django
        location / {
            proxy_pass         http://django;
            proxy_set_header   Host              $host;
            proxy_set_header   X-Real-IP         $remote_addr;
            proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto $scheme;
            proxy_read_timeout 90s;
        }
    }
}
```

## Network Access

| Access | URL |
|--------|-----|
| External (host) | http://localhost |
| Internal (Docker) | http://obs-nginx:80 |

## Request Flow

### Static Files

```
Request: /static/admin/css/base.css
         │
         ▼
Nginx matches: location /static/
         │
         ▼
Serve from: /app/static/admin/css/base.css
         │
         ▼
Response: 200 OK (from volume)
```

### Media Files

```
Request: /media/uploads/image.jpg
         │
         ▼
Nginx matches: location /media/
         │
         ▼
Serve from: /app/mediafiles/uploads/image.jpg
         │
         ▼
Response: 200 OK (from volume)
```

### Dynamic Requests

```
Request: /todo/
         │
         ▼
Nginx matches: location /
         │
         ▼
Proxy to: http://django (obs-django:9000)
         │
         ▼
Django processes request
         │
         ▼
Response: 200 OK (HTML)
```

## Useful Commands

### Container Management

```bash
# Restart Nginx
docker compose -f django_app/docker-compose.yml restart obs-nginx

# View logs
docker logs -f obs-nginx

# Access shell
docker exec -it obs-nginx /bin/sh

# Reload config (without restart)
docker exec obs-nginx nginx -s reload

# Test config
docker exec obs-nginx nginx -t
```

### Test Requests

```bash
# Test home page
curl -I http://localhost/

# Test static files
curl -I http://localhost/static/admin/css/base.css

# Test media files
curl -I http://localhost/media/

# Test proxy to Django
curl -I http://localhost/admin/
```

## Expected Output

### Nginx Logs

```bash
$ docker logs obs-nginx

172.18.0.1 - - [15/Mar/2026:10:30:00 +0000] "GET / HTTP/1.1" 200 2048 "-" "Mozilla/5.0"
172.18.0.1 - - [15/Mar/2026:10:30:01 +0000] "GET /static/style.css HTTP/1.1" 200 1234 "http://localhost/" "Mozilla/5.0"
```

### Config Test

```bash
$ docker exec obs-nginx nginx -t

nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

## API Endpoints

Nginx handles these paths:

| Path | Handler | Backend |
|------|---------|---------|
| `/` | Proxy | Django |
| `/admin/` | Proxy | Django |
| `/todo/` | Proxy | Django |
| `/api/` | Proxy | Django |
| `/static/*` | Serve | Volume |
| `/media/*` | Serve | Volume |
| `/site-static/*` | Serve | Volume |

## Health Checks

```bash
# Test if Nginx is responding
curl -f http://localhost/ || echo "Nginx is down"

# Check Nginx status
docker exec obs-nginx nginx -v

# Check worker processes
docker exec obs-nginx ps aux | grep nginx
```

## Configuration Files

| File | Path | Purpose |
|------|------|---------|
| nginx.conf | nginx/nginx.conf | Nginx configuration |

## Integration Points

| Service | Connection | Purpose |
|---------|------------|---------|
| Django | Proxy to :9000 | Application backend |
| Static files | Volume mount | Served directly |
| Media files | Volume mount | Served directly |

## Troubleshooting

### 502 Bad Gateway

```bash
# Check if Django is running
docker ps | grep obs-django

# Test Django directly
curl http://localhost:9000/

# Check Nginx logs
docker logs obs-nginx | tail -20

# Restart both
docker compose -f django_app/docker-compose.yml restart obs-django obs-nginx
```

### Static Files Not Loading

```bash
# Check static volume is mounted
docker inspect obs-nginx | jq '.[0].Mounts'

# Check static files exist
docker exec obs-nginx ls -la /app/static/

# Rebuild static files
docker exec obs-django python manage.py collectstatic --noinput
```

### 404 Errors

```bash
# Check location paths in nginx.conf
docker exec obs-nginx cat /etc/nginx/nginx.conf | grep location

# Verify file paths match
docker exec obs-nginx ls -la /app/static/
docker exec obs-nginx ls -la /app/mediafiles/
```

## Quick Reference

### Docker Commands

```bash
# Start
docker compose -f django_app/docker-compose.yml up -d obs-nginx

# Stop
docker compose -f django_app/docker-compose.yml stop obs-nginx

# Restart
docker compose -f django_app/docker-compose.yml restart obs-nginx

# View logs
docker logs -f obs-nginx

# Reload config
docker exec obs-nginx nginx -s reload
```

### URLs

| Service | URL |
|---------|-----|
| Nginx | http://localhost |
| Django (direct) | http://localhost:9000 |

### Key Ports

| Port | Service |
|------|---------|
| 80 | HTTP |

### Location Paths

| Path | Purpose |
|------|---------|
| `/` | Django app |
| `/static/` | Django static files |
| `/media/` | User uploads |
| `/site-static/` | Site static (no collectstatic) |

### Upstream Config

```nginx
upstream django {
    server obs-django:9000;
}
```

---

## Related Documentation

- [Django App](./01-django-app.md) - Backend application
