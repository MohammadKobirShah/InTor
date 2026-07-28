# 🇮🇳 #1 Indian Proxy Platform, Pro REST API Suite & #1 Bug Bounty Scanner

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/Node.js-%3E%3D18.0.0-green.svg)](package.json)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](docker-compose.yml)
[![Protocol: HTTP & SOCKS5](https://img.shields.io/badge/Protocol-HTTP%20%7C%20SOCKS5-orange.svg)](#features)

> **আপনার টার্গেট #1 করা! (Live Active-Only Pool, Auto-Harvesting Every 60s, Dynamic Domain Detection & Deep Bug Bounty Suite)**  
> A complete enterprise-grade proxy harvesting, verification, routing, and security auditing platform designed for developers, scrapers, and security professionals.

---

## 🌟 Key Features (#1 Enterprise & Pro-Grade Suite)

1. **Active/Live Proxies by Default (Zero Stale IPs)**:
   * All API routes and dashboard tables default to `status=online` — guaranteeing 100% verified working Indian proxies.
2. **Automated Background Harvester (Every Minute Auto)**:
   * A background worker (`autoPoolUpdater`) runs every **60 seconds (1 minute)** to harvest new public proxies, verify Indian geolocation (`countryCode === 'IN'`), test latency & speeds, and prune offline IPs.
3. **Dynamic Hosted Domain Detection (No Hardcoded Localhost)**:
   * The Dark-Mode Web Admin Dashboard (`public/index.html`) automatically detects `window.location.origin` and `window.location.hostname` — displaying dynamic integration snippets for whatever domain or cloud host you deploy on!
4. **Multi-Category Indian Proxy Pool**:
   * **4G/5G Mobile Cellular** (*Reliance Jio 5G*, *Bharti Airtel 4G LTE*, *Vi Mobile*).
   * **Residential FTTH & Broadband** (*JioFiber*, *Airtel Xstream*, *ACT Fibernet*, *BSNL FTTH*).
   * **Datacenter & Cloud Hosting** (*Tata Communications*, *Sify Technologies*).
   * **Tor Indian Exit Node Cluster** (*Enforced `ExitNodes {in}` with direct SOCKS5 and HTTP Privoxy bridge*).
5. **Dual-Protocol Support**: Seamlessly supports both **HTTP / HTTPS** and **SOCKS4 / SOCKS5** proxies.
6. **Smart Rotational Gateway (Port `8899`)**: Point any scraper, bot, or browser automation script to port `8899` — every request is dynamically routed through the highest-scoring Indian proxy in the pool!
7. **Pro REST API Suite (`/api/v1/proxies`)**:
   * Dedicated semantic routes for `/residential`, `/mobile`, `/datacenter`, `/tor`, custom ISP `/isp/:ispName`, and plain-text `/export?format=txt`.
8. **Interactive Dark-Mode Web Admin Dashboard**:
   * Filter by Proxy Type, Protocol, City, and ISP with 0ms client-side latency.
   * Visual badges for `MOBILE`, `RESIDENTIAL`, `DATACENTER`, `TOR`.
   * One-click copy buttons with Toast alerts and `.TXT` export.
9. **#1 Bug Bounty Automated Audit & Vulnerability Scanner (`bug_bounty_scanner.py`)**:
   * Deep 10-module security scanning suite checking Security Headers (`CWE-693`), CORS (`CWE-942`), Auth (`CWE-306`), SSRF (`CWE-918`), XSS (`CWE-79`), SQLi/NoSQLi (`CWE-89`), Rate Limiting & DoS (`CWE-400`), LFI/Traversal (`CWE-22`), Verb Tampering (`CWE-650`), and JSON exception handling (`CWE-915`).

---

## 📁 Repository Directory Tree

```
indian-proxy-platform-pro/
├── README.md                          # Primary project documentation & architecture guide
├── LICENSE                            # MIT License
├── .gitignore                         # Build and log exclusion rules
├── Dockerfile                         # Node.js 20 Alpine + Tor + Privoxy container spec
├── docker-compose.yml                 # Multi-server cluster orchestration (3 Tor Workers + API + Gateway)
├── entrypoint.sh                      # Clean daemon startup & socket readiness script
├── package.json                       # Node.js project manifest & dependencies
├── allowed_247_channels.json          # Streaming channel configuration
├── src/
│   ├── api_server.js                  # Enterprise REST API & Dashboard Server (Port 8000)
│   ├── rotation_gateway.js            # Smart Rotational HTTP/SOCKS Proxy Gateway (Port 8899)
│   ├── checker_engine.js              # Pro-grade geo-IP verification & Auto-Harvester engine (Every 60s)
│   └── proxy_pool.json                # Pre-loaded database of verified Indian proxies
├── public/
│   └── index.html                     # Interactive Dark-Mode Web Admin Dashboard (Dynamic Domain Detection)
├── bug_bounty_scanner.py              # #1 Enterprise Bug Bounty Security Audit Scanner
├── proxy_tester.py                    # Standalone CLI Proxy Latency & Download Speed Tester
├── DOCKER_INDIAN_PROXY_SETUP.md       # Docker container & Tor-Privoxy bridge documentation
├── INDIAN_PROXY_PLATFORM_PRO.md       # Pro REST API reference & Bengali/English developer guide
└── BUG_BOUNTY_AUDIT_REPORT.md         # Deep automated security audit & vulnerability report
```

---

## 🚀 Quickstart Guide

### 1. Launch with Node.js directly
```bash
# Install dependencies
npm install

# Start the Pro API Server & Admin Dashboard (Port 8000) + Smart Rotational Gateway (Port 8899)
node src/api_server.js
```
* **REST API Endpoints**: `http://localhost:8000/api/v1/proxies` (or your hosted origin)
* **Web Admin Dashboard**: `http://localhost:8000/` (or your hosted origin)
* **Smart Rotation Gateway**: `http://localhost:8899/`

### 2. Launch Complete Multi-Server Cluster with Docker Compose
To deploy **3 Tor Indian Exit instances** (`in-tor-1..3`), the **REST API**, and the **Rotational Gateway** concurrently:
```bash
docker-compose up -d --build
```
* **Tor SOCKS5 Ports**: `0.0.0.0:9050`, `9051`, `9052`
* **Tor Privoxy HTTP Ports**: `0.0.0.0:8118`, `8119`, `8120`

### 3. Cloud Deployment (Render.com / Heroku / Railway / Fly.io)
On cloud platforms that only expose a single web port (e.g. `intor2.onrender.com`), use our **Single-Port Transparent Proxy Gateway** or **REST Fetch API**:
```bash
# 1. Single-Port cURL Proxying (Directly over standard port 80/443 on Render)
curl -x https://intor2.onrender.com "http://ip-api.com/json/"

# 2. REST Proxy Fetch Endpoint (Alternative for browsers & GET scrapers)
curl "https://intor2.onrender.com/api/v1/fetch?url=http://ip-api.com/json/"
```

---

## 📡 Pro REST API Routes (বাংলা ও ইংরেজি রেফারেন্স)

| HTTP Method | API Endpoint | Description |
| :---: | :--- | :--- |
| `GET` | `/api/v1/proxies` | List all Indian proxies with filtering (`type`, `protocol`, `city`, `isp`, `minScore`) |
| `GET` | `/api/v1/proxies/residential` | Only Residential FTTH/Broadband proxies (*JioFiber*, *Airtel Xstream*) |
| `GET` | `/api/v1/proxies/mobile` | Only 4G/5G Mobile Cellular proxies (*Jio 5G*, *Airtel 4G*) |
| `GET` | `/api/v1/proxies/datacenter` | Only Datacenter / Cloud hosting proxies (*Tata*, *Sify*) |
| `GET` | `/api/v1/proxies/tor` | Only Tor Indian Exit Node proxies (*High Anonymity*) |
| `GET` | `/api/v1/proxies/isp/:ispName` | Custom ISP lookup (e.g., `/isp/jio`, `/isp/airtel`, `/isp/bsnl`) |
| `GET` | `/api/v1/proxies/export?format=txt` | Plain-text `.TXT` export (`ip:port` or `socks5://ip:port`) for scrapers |
| `GET` | `/api/v1/proxies/random` | Select a single random high-scoring Indian proxy |
| `GET` | `/api/v1/stats` | Comprehensive pool analytics, state/city breakdown & type distribution |
| `POST` | `/api/v1/proxies/check` | Trigger real-time background health & geo-verification sweep |
| `POST` | `/api/v1/proxies/add` | Dynamically add custom proxy URLs into the pool |

### Example cURL Commands (Using Dynamic Domain Origin)
```bash
# 1. Get only 4G/5G Mobile SOCKS5 proxies in Mumbai
curl "https://your-domain.com/api/v1/proxies/mobile?city=Mumbai&protocol=socks5"

# 2. Get only Reliance Jio proxies across all categories
curl "https://your-domain.com/api/v1/proxies/isp/jio"

# 3. Export all Residential proxies as a clean plain-text list (.txt)
curl "https://your-domain.com/api/v1/proxies/export?format=txt&type=residential"
```

---

## 🔄 Smart Rotational Gateway (`:8899`) Integration

Point your scrapers to **port `8899`** on your host — every HTTP request will automatically be proxied through the highest-scoring Indian proxy in the pool:

### Python (Requests / Scrapy)
```python
import requests

# Replace with your server's hostname or IP
gateway_url = "http://your-hostname:8899"
proxies = {
    "http": gateway_url,
    "https": gateway_url
}

response = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=10)
print("Rotated Indian IP:", response.json().get("query"))
print("ISP:", response.json().get("isp"), "| City:", response.json().get("city"))
```

---

## 🛡️ #1 Bug Bounty Automated Scanner (`bug_bounty_scanner.py`)

Run deep security auditing and vulnerability scanning against your API or target web application:
```bash
# Run 10-module deep audit against target application
python3 bug_bounty_scanner.py --target http://localhost:8000 --output report.json

# Run audit routed through your Indian Smart Rotational Gateway
python3 bug_bounty_scanner.py --target http://localhost:8000 --proxy http://localhost:8899
```
* For full findings and remediation instructions, inspect **[`BUG_BOUNTY_AUDIT_REPORT.md`](BUG_BOUNTY_AUDIT_REPORT.md)**.
