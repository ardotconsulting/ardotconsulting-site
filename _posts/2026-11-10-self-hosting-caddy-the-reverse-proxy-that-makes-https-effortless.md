---
layout: post
title: "Self-Hosting Caddy: The Reverse Proxy That Makes HTTPS Effortless"
date: 2026-11-10
author: "ARDOT Consulting"
tags: [caddy, reverse-proxy, https, self-hosting, docker, tls, ssl]
excerpt: "Replace your complex nginx + Certbot setup with Caddy, an open source web server that handles TLS certificates and reverse proxying automatically."
---

If you're self-hosting any services, you've probably hit the same wall: getting HTTPS working is a chore. You need a web server, a certificate manager, a renewal cron job, and configuration files that look like they were written in hieroglyphics. The standard nginx + Certbot combo works, but it's fragile. Renewals fail silently. Configs break on updates. Every new subdomain means repeating the whole dance.

Caddy is an open source web server written in Go that handles TLS certificates and reverse proxying automatically. You point it at a domain, and it obtains, installs, and renews your Let's Encrypt certificates without scripts, cron jobs, or manual intervention. It's the piece of infrastructure you forget about, which is exactly what infrastructure should be.

## What Is Caddy?

Caddy is an open source web server with built-in automatic HTTPS. Released in 2015 and actively maintained (v2.11.9 as of November 2026), it's written in Go and ships as a single binary with no runtime dependencies. The project has over 78,000 stars on GitHub and is licensed under Apache 2.0.

It serves two main roles in a self-hosted stack:

1. **Reverse proxy** — sits in front of your Docker containers and routes traffic by domain name
2. **Static file server** — serves websites directly, similar to nginx or Apache

What sets Caddy apart is that it obtains and renews TLS certificates from Let's Encrypt (or ZeroSSL) by default. No Certbot. No cron jobs. No certbot renew hooks. You write a Caddyfile with your domain name, start Caddy, and HTTPS works.

## Why Self-Host Your Reverse Proxy?

### Automatic Certificate Management

The biggest pain point in self-hosting is TLS. Every service you expose needs a certificate. With nginx, you configure Certbot, set up renewal hooks, and hope nothing breaks. With Caddy, certificates are automatic. It handles the ACME challenge, stores the certificate, and renews it before expiry. If a renewal fails, it retries. You don't think about certificates again.

### Minimal Configuration

A complete reverse proxy config in Caddy can be two lines. The equivalent nginx config with SSL, proxy headers, and Certbot integration is 20+ lines across multiple files. Less configuration means fewer mistakes and faster onboarding when you add a new service.

### Single Binary, No Dependencies

Caddy is a single Go binary with no Python runtime, shared libraries, or package dependencies. Download it, run it, done. Upgrading means replacing one file. This makes it ideal for Docker or a bare VPS.

## Caddy vs Nginx + Certbot: Feature Comparison

| Feature | Caddy | Nginx + Certbot |
|---------|-------|-----------------|
| Automatic HTTPS | Built-in, zero config | Requires Certbot setup |
| Certificate renewal | Automatic, built-in | Cron job + renewal hooks |
| HTTP/3 support | Enabled by default | Requires custom build + config |
| Configuration format | Caddyfile (human-friendly) | nginx.conf (complex syntax) |
| Runtime dependencies | Single binary | nginx + Python (Certbot) |
| Config reload | Zero-downtime, automatic on file change | `nginx -s reload` (manual) |
| Administration API | REST API on port 2019 | None |
| Reverse proxy | Native directive | Native directive |
| Static file serving | Yes | Yes |
| Internal PKI / CA | Built-in | Not available |
| On-Demand TLS (custom domains) | Yes | No |
| License | Apache 2.0 | BSD-2 + GPL (Certbot is GPL) |
| Community | 78k+ GitHub stars | 50k+ (nginx), 31k+ (Certbot) |
| Learning curve | Low | Medium to high |

## Hardware Requirements

Caddy is written in Go and compiled to native code, so it uses minimal resources compared to nginx + Certbot + Python.

| Setup | RAM | CPU | Disk | Notes |
|-------|-----|-----|------|-------|
| Personal / 1-5 sites | 50-100 MB | 1 core | 512 MB | Runs on a $4/mo VPS |
| Small business / 10-30 sites | 100-256 MB | 1-2 cores | 1 GB | Handles moderate traffic |
| High traffic / 50+ sites | 256-512 MB | 2-4 cores | 2 GB | Add more CPU for TLS handshakes |
| Enterprise / 500+ sites | 512 MB+ | 4+ cores | 4 GB+ | Use On-Demand TLS, cluster mode |

Caddy's memory footprint stays low because it doesn't have a Python runtime or plugin system loaded into memory. The Go binary is self-contained.

## Step-by-Step Docker Setup

The cleanest way to run Caddy alongside your other self-hosted services is with Docker Compose. Here's a complete setup that puts Caddy in front of multiple services.

### Step 1: Create the directory structure

```bash
mkdir -p ~/caddy/{caddy_data,caddy_config}
cd ~/caddy
```

### Step 2: Write the Caddyfile

Create a file named `Caddyfile` in the `caddy_config` directory:

```bash
cat > caddy_config/Caddyfile << 'EOF'
# Your main site
example.com {
    reverse_proxy nextcloud:80
}

# Subdomain routing to other services
chat.example.com {
    reverse_proxy mattermost:8000
}

# Another service with additional headers
analytics.example.com {
    reverse_proxy plausible:8000 {
        header_up X-Real-IP {remote_host}
    }
}
EOF
```

Replace `example.com` with your actual domain. Each block is a site definition. The domain name on the first line tells Caddy which domain to serve and which certificate to obtain.

### Step 3: Write the docker-compose.yml

```yaml
version: "3.8"

services:
  caddy:
    image: caddy:2-alpine
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"  # HTTP/3 support
    volumes:
      - ./caddy_config/Caddyfile:/etc/caddy/Caddyfile
      - ./caddy_data:/data
      - ./caddy_config:/config
    networks:
      - caddy_net

  # Example service: Nextcloud
  nextcloud:
    image: nextcloud:apache
    container_name: nextcloud
    restart: unless-stopped
    volumes:
      - nextcloud_data:/var/www/html
    networks:
      - caddy_net

  # Example service: Mattermost
  mattermost:
    image: mattermost/mattermost-team-edition:latest
    container_name: mattermost
    restart: unless-stopped
    volumes:
      - mattermost_data:/mattermost/data
    networks:
      - caddy_net

volumes:
  nextcloud_data:
  mattermost_data:

networks:
  caddy_net:
    driver: bridge
```

Caddy and your services share the `caddy_net` Docker network. Caddy references them by container name in the Caddyfile (e.g., `nextcloud:80`). No ports need to be exposed on the individual services because Caddy handles all external traffic.

### Step 4: Point your DNS

Before starting Caddy, create A records for each subdomain pointing to your server's IP address:

| Subdomain | Record Type | Value |
|-----------|-------------|-------|
| example.com | A | your.server.ip |
| chat.example.com | A | your.server.ip |
| analytics.example.com | A | your.server.ip |

Caddy needs DNS to resolve before completing the ACME challenge. If DNS isn't ready, Caddy retries automatically once it propagates.

### Step 5: Start the stack

```bash
docker compose up -d
```

Watch the logs to see Caddy obtain certificates:

```bash
docker logs -f caddy
```

You should see output like:

```
certificate obtained successfully
serving initial configuration
```

Within seconds, all three sites are live with valid HTTPS certificates. No Certbot commands. No nginx config files. No cron jobs.

### Step 6: Open the firewall

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 443/udp
```

Port 80 is needed for the ACME HTTP challenge and HTTP-to-HTTPS redirects. Port 443 for HTTPS traffic. Port 443/udp for HTTP/3.

### Step 7: Verify

```bash
curl -sI https://example.com
```

A `200 OK` or `301` response means Caddy is running and serving HTTPS.

### Step 8: Add a new service later

To add a new service, add a block to the Caddyfile and a service to docker-compose.yml, then:

```bash
docker compose up -d
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```

Caddy reloads with zero downtime. Existing connections stay alive while the new config takes effect. You can also just restart the container.

## Configuration Details

### The Caddyfile Format

Caddy uses a configuration format called the Caddyfile, designed to be readable without a reference manual. Here's a more complete example showing common patterns:

```caddyfile
{
    # Global options
    email admin@example.com
    admin off
}

example.com {
    # Redirect www to non-www
    www.example.com {
        redir https://example.com{uri} 308
    }

    # Serve static files from a directory
    root * /var/www/html
    file_server

    # Enable gzip compression
    encode gzip zstd
}

api.example.com {
    # Reverse proxy with WebSocket support (automatic)
    reverse_proxy backend:3000

    # Rate limiting (requires caddy-ratelimit module)
    # rate_limit {
    #     zone dynamic {
    #         key {remote_host}
    #         events 10
    #         window 1s
    #     }
    # }
}

# Internal service, no public cert needed
internal.local {
    reverse_proxy dashboard:8080
    tls internal
}
```

The `tls internal` directive tells Caddy to use its built-in CA instead of Let's Encrypt, useful for internal services without public DNS records.

### Environment Variables in the Caddyfile

Caddy supports environment variable substitution, useful for Docker deployments:

```caddyfile
{$DOMAIN} {
    reverse_proxy {$UPSTREAM_HOST}:{$UPSTREAM_PORT}
}
```

Then in your docker-compose.yml:

```yaml
environment:
  - DOMAIN=example.com
  - UPSTREAM_HOST=nextcloud
  - UPSTREAM_PORT=80
```

This lets you use the same Caddyfile across deployments by changing environment variables.

## Optional Features

### HTTP/3 Support

Caddy supports HTTP/3 (QUIC) out of the box. It's enabled by default when you expose port 443/udp. Browsers that support HTTP/3 automatically use it, with fallback to HTTP/2 for those that don't.

### Basic Authentication

Protect a service with a username and password:

```caddyfile
admin.example.com {
    basicauth {
        admin $2a$14$YourHashedPasswordHere
    }
    reverse_proxy admin_panel:8080
}
```

Generate the hashed password with `docker exec caddy caddy hash-password --plaintext "yourpassword"`.

### Access Logging

Enable structured logging for any site:

```caddyfile
example.com {
    log {
        output file /data/access.log
        format json
    }
    reverse_proxy nextcloud:80
}
```

Logs in JSON format are easy to parse with `jq` or feed into a logging stack like Loki or Grafana.

### Custom Headers and Security

Add security headers in one block:

```caddyfile
example.com {
    header {
        Strict-Transport-Security "max-age=31536000"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
    }
    reverse_proxy nextcloud:80
}
```

### On-Demand TLS

If you run a SaaS platform where customers use their own domains, Caddy's On-Demand TLS provisions certificates on-the-fly during the TLS handshake. Caddy calls an API endpoint you specify to verify the domain is allowed before issuing a certificate. This lets you serve thousands of custom domains without pre-configuring each one.

## Security Checklist

| Item | Action | Priority |
|------|--------|----------|
| Admin API | Set `admin off` or bind to localhost only | High |
| Firewall | Allow only ports 80, 443, 443/udp | High |
| Rate limiting | Use the caddy-ratelimit module for public APIs | Medium |
| Access logs | Enable structured logging for audit trails | Medium |
| HSTS header | Add Strict-Transport-Security header | High |
| Certificate storage | Mount `/data` on persistent volume | High |
| Updates | Pull new Caddy image monthly | Medium |
| DNS CAA | Add CAA records restricting CA to Let's Encrypt | Low |
| OCSP stapling | Enabled by default, verify in logs | Low |
| TLS versions | Caddy defaults to TLS 1.2+ (compliant with PCI, HIPAA, NIST) | Already done |

Caddy's TLS defaults pass PCI, HIPAA, and NIST compliance requirements out of the box. You don't need to manually configure cipher suites or protocol versions.

## Cost Comparison

| Component | Caddy (self-hosted) | Nginx + Certbot (self-hosted) | Cloudflare (managed) |
|-----------|--------------------|-----------------------------|--------------------|
| Software cost | $0 (Apache 2.0) | $0 (open source) | $0 (free tier) |
| VPS (2GB RAM) | $8/mo | $8/mo | $8/mo |
| TLS certificates | $0 (Let's Encrypt) | $0 (Let's Encrypt) | $0 (Cloudflare) |
| Maintenance time | ~1 hr/month | ~3-4 hr/month | ~0.5 hr/month |
| HTTP/3 support | Included | Custom build required | Included |
| DDoS protection | None (add separately) | None (add separately) | Included (free tier) |
| Data sovereignty | Full control | Full control | Cloudflare sees traffic |
| Vendor lock-in | None | None | Moderate |

The real cost difference is maintenance time. Caddy's automatic certificate management eliminates the most common source of downtime in self-hosted stacks: expired or failed certificate renewals.
## When It Might NOT Be Right

Caddy isn't the right choice for every situation:

- **Existing nginx expertise**: If your team knows nginx inside and out, switching has a learning cost. The Caddyfile is simpler, but migrating existing configs takes time.
- **Complex rewrite rules**: Nginx's rewrite engine is more mature for edge cases like conditional rewrites based on request headers, user agents, or geographic IP rules. Caddy can do most of this, but the syntax is less battle-tested.
- **Module ecosystem**: Nginx has a larger third-party module ecosystem. Caddy's module system is extensible (build custom modules in Go), but the community library is smaller.
- **No built-in WAF**: Caddy doesn't include a web application firewall. If you need request filtering, bot protection, or SQL injection detection, add a separate tool like CrowdSec or Coraza.

## Integrations With Other Self-Hosted Tools

Caddy is the glue that holds a self-hosted stack together. Every service you deploy needs to be exposed securely, and Caddy handles that:

- **Caddy + Nextcloud**: Proxy traffic to your Nextcloud container with automatic TLS. See our [Nextcloud guide](/blog/2026/10/06/self-hosting-nextcloud-replace-google-workspace-with-your-own-file-sync-and-collaboration-platform/).
- **Caddy + Mattermost**: Route `chat.example.com` to Mattermost with automatic WebSocket support. See our [Mattermost guide](/blog/2026/10/08/self-hosting-mattermost-replace-slack-with-your-own-team-chat-platform/).
- **Caddy + Metabase**: Proxy your analytics dashboard behind HTTPS. See our [Metabase guide](/blog/2026/09/30/self-hosting-metabase-open-source-business-analytics-without-saas/).
- **Caddy + Vaultwarden**: Caddy is the recommended reverse proxy for Vaultwarden because it handles WebSocket connections natively. See our [Vaultwarden guide](/blog/2026/10/16/self-hosting-vaultwarden-replace-lastpass-with-your-own-password-manager/).

The pattern is always the same: add a Caddyfile block with your domain and container name, reload Caddy, and your service is live on HTTPS.

## Migration From Nginx + Certbot

If you're already running nginx with Certbot, here's a transition plan:

1. **Install Caddy alongside nginx** on a different port (e.g., `:8443`) to test your config. Use `tls internal` to avoid conflicts with existing certificates.
2. **Translate your nginx configs** to Caddyfile blocks. Most reverse proxy configs map directly: `proxy_pass` becomes `reverse_proxy`, `server_name` becomes the site label.
3. **Test each site** on the alternate port to verify routing and headers work correctly.
4. **Schedule a maintenance window** (5 minutes is enough).
5. **Stop nginx**, start Caddy on ports 80/443. Caddy obtains new certificates immediately.
6. **Verify all sites** are accessible via HTTPS, including WebSocket connections for services like Mattermost.
7. **Remove Certbot cron jobs** and uninstall Certbot.
8. **Remove nginx config files** after a few days of stable operation.

The migration is typically fast because Caddyfile syntax is so much simpler. A 200-line nginx config often becomes a 30-line Caddyfile.

## Wrapping Up

Caddy fills a specific gap in the self-hosting stack: it makes the part that's supposed to be boring actually boring. TLS certificates, reverse proxying, HTTP/3, security headers, and zero-downtime reloads all work without you thinking about them.

The worst case is a few hours learning the Caddyfile syntax and migrating configs. The best case is never thinking about certificates or renewal failures again. For most self-hosted setups, that tradeoff is a clear win.

If you're building a self-hosted stack, Caddy should be the first container you deploy. Everything else sits behind it.

---

*Want help setting up Caddy or planning your self-hosted infrastructure? [Get in touch with ARDOT Consulting](/) — we specialize in open source automation and self-hosting for small businesses.*
