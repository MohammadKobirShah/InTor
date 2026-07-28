# 🇮🇳 Deep Research & Architectural Whitepaper: Rotating Proxies on Single-Port PaaS (Render.com, Heroku & Vercel)

> **Render.com-এ সিঙ্গেল পোর্টে রোটিং প্রক্সি কীভাবে কাজ করে? (Deep Research & Analysis)**  
> This whitepaper explains the network mechanics of cloud load balancers, why secondary ports and HTTP `CONNECT` verbs fail on Render.com, and how our **Single-Port Rotating REST Gateway (`/api/v1/rotate`)** solves this 100%.

---

## 1. The Core Network Problem on Render.com

When developers try to use traditional proxy commands on Render:
```bash
# ✗ Fails on Render (Port 8899 is blocked by Render's firewall)
curl -x http://intor2.onrender.com:8899 "http://ip-api.com/json/"

# ✗ Fails for HTTPS targets on Render (Render's Edge Proxy rejects the HTTP CONNECT verb)
curl -x https://intor2.onrender.com "https://ip-api.com/json/"
```

### Why does this happen?
1. **Single-Port Edge Routing**: Render Web Services only route **one public HTTP/HTTPS port (`80` / `443`)** through their Edge Envoy load balancers to your container's internal `PORT` (`8000`). Secondary TCP ports (`8899`, `9050`, `8118`) are strictly firewalled from the public internet.
2. **TLS Termination & `CONNECT` Rejection**: Traditional HTTPS proxying requires sending an HTTP `CONNECT host:443` method to establish a raw TCP tunnel. Cloud load balancers (Render, Heroku, AWS ALB) terminate SSL at the edge and **reject `CONNECT` verbs**, making traditional `-x` proxying for HTTPS targets impossible.

---

## 2. The Pro-Level Solution: Rotating REST Gateway (`/api/v1/rotate`)

How do commercial enterprise proxy platforms (**ScrapingBee, ZenRows, ScraperAPI**) operate on cloud infrastructure? They use an **HTTP REST Gateway over standard Port 443**:

```
===================================================================================================
                             HOW ROTATING PROXIES WORK ON RENDER.COM
===================================================================================================

  [ Client / Scraper / Bot ]
              ||
              || 1. Standard HTTP GET / POST Request over Port 443 (100% Allowed by Render)
              ||    https://intor2.onrender.com/api/v1/rotate?url=https://ip-api.com/json/&type=residential
              \/
  +-----------------------------------------------------------------------------------------------+
  | RENDER.COM EDGE LOAD BALANCER (Port 443 -> Internal Port 8000)                                |
  +-----------------------------------------------------------------------------------------------+
              ||
              || 2. Forwards clean HTTP request to Node.js Express Server
              \/
  +-----------------------------------------------------------------------------------------------+
  | NODE.JS ENTERPRISE SERVER (src/api_server.js on PORT 8000)                                    |
  |                                                                                               |
  |  • Parses target URL:    "https://ip-api.com/json/"                                           |
  |  • Parses target rule:   type = "residential" (or "mobile", "tor", "datacenter", "all")       |
  |  • Selects best proxy:   src/premium_proxy_gateway.js selects online Indian proxy             |
  +-----------------------------------------------------------------------------------------------+
              ||
              || 3. Outbound Request from inside Render container through Indian Proxy Pool
              \/
  +-----------------------------------------------------------------------------------------------+
  | INDIAN PROXY POOL (Jio 5G Mobile / Airtel FTTH / Tor Exit Node)                               |
  +-----------------------------------------------------------------------------------------------+
              ||
              || 4. Exits with 100% Indian IP Address (Target website sees India, NOT Render!)
              \/
     [ TARGET WEBSITE: https://ip-api.com/json/ ]
===================================================================================================
```

---

## 3. Why This Architecture is #1 for Render / Cloud PaaS

| Feature | Traditional `-x` Proxy on Render | Our `/api/v1/rotate` REST Gateway |
| :--- | :---: | :---: |
| **Requires Secondary TCP Port (`8899`)** | Yes *(Blocked by Render)* | **No** *(Uses standard Port 443)* |
| **Works for HTTP Targets (`http://`)** | Partial | **100% Reliable** |
| **Works for HTTPS Targets (`https://`)** | No *(Render rejects `CONNECT`)* | **100% Reliable** |
| **Supports BrightData/Oxylabs Targeting** | No | **Yes (`?type=residential`, `?city=mumbai`)** |
| **Zero Firewall Blocking** | No | **Yes (Standard HTTPS traffic)** |

---

## 4. Code Examples for Your Render Deployment (`intor2.onrender.com`)

### 1. cURL (Terminal / Shell)
```bash
# Rotate via Residential FTTH Pool:
curl "https://intor2.onrender.com/api/v1/rotate?url=http://ip-api.com/json/&type=residential"

# Rotate via Datacenter Pool:
curl "https://intor2.onrender.com/api/v1/rotate?url=http://ip-api.com/json/&type=datacenter"

# Rotate via All (Any Live Indian Proxy):
curl "https://intor2.onrender.com/api/v1/rotate?url=http://ip-api.com/json/&type=all"
```

### 2. Python (Requests / Scrapy / BeautifulSoup)
```python
import requests

# Set your Render endpoint and targeting rules
render_gateway = "https://intor2.onrender.com/api/v1/rotate"
params = {
    "url": "http://ip-api.com/json/",
    "type": "mobile",       # Options: 'residential', 'datacenter', 'tor', 'mobile', 'all'
    "city": "Mumbai"        # Optional city targeting
}

response = requests.get(render_gateway, params=params, timeout=15)
data = response.json()

print("Rotated Indian IP:", data.get("query"))
print("ISP / Carrier:", data.get("isp"), "| City:", data.get("city"))
print("Proxy Score:", response.headers.get("X-Indian-Proxy-Score"))
```

### 3. Node.js (Axios / Puppeteer API Fetch)
```javascript
const axios = require('axios');

async function scrapeViaRenderGateway() {
  const res = await axios.get('https://intor2.onrender.com/api/v1/rotate', {
    params: {
      url: 'http://ip-api.com/json/',
      type: 'residential'
    }
  });

  console.log('Rotated Indian IP:', res.data.query);
  console.log('ISP:', res.data.isp, '| City:', res.data.city);
  console.log('Proxy ID Used:', res.headers['x-indian-proxy-id']);
}

scrapeViaRenderGateway();
```
