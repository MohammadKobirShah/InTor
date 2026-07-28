# Indian Tor + Privoxy Residential Proxy Caching Server (Docker Setup)

This repository containerizes a **24/7 Channel Stream Caching Server** (`server.js`) that automatically routes all outbound stream fetches through **Indian Tor Exit Nodes (`IN`)** using an integrated **Privoxy HTTP-to-SOCKS5 bridge**.

---

## 1. Architecture Overview

```
+---------------------------------------------------------------------------------+
| Docker Container (node:20-alpine)                                              |
|                                                                                 |
|  +--------------------+       +----------------------+       +---------------+  |
|  | Node.js Server     | ====> | Privoxy (HTTP Proxy) | ====> | Tor (SOCKS5)  |  |
|  | (Express :7890)    | HTTP  | (127.0.0.1:8118)     | SOCKS5| (127.0.0.1:9050)|
|  +--------------------+       +----------------------+       +---------------+  |
|          |                                                           ||         |
|          +--- Cache Reads/Writes ---> [ /cache_segments ]            ||         |
+----------------------------------------------------------------------||---------+
                                                                       \/
                                                       +--------------------------+
                                                       | Indian Tor Exit Node(IN) |
                                                       +--------------------------+
```

1. **Tor Daemon**:
   - Enforces `ExitNodes {in}` and `StrictNodes 1` so outbound traffic always exits from India.
   - Listens on SOCKS5 port `127.0.0.1:9050`.
   - Runs under non-privileged user `tor`.
2. **Privoxy HTTP Bridge**:
   - Converts the Tor SOCKS5 proxy into a standard HTTP/HTTPS proxy listening on `127.0.0.1:8118`.
   - Configured via `forward-socks5t / 127.0.0.1:9050 .`.
3. **Node.js Caching Server (`server.js`)**:
   - Uses `http-proxy-agent` and `https-proxy-agent` pointed at `INDIAN_PROXY="http://127.0.0.1:8118"`.
   - Proxies and caches media segment files (`.m3u8` / `.ts` / `.m4s`) into `cache_segments/`.

---

## 2. Key Improvements & Fixes in `Dockerfile`

| Area | Issue in Original Paste | Corrected Implementation |
| :--- | :--- | :--- |
| **Environment Variable** | Contained markdown link artifact: `INDIAN_PROXY="[http://127.0.0.1:8118](...)"` | Cleaned to valid URL syntax: `ENV INDIAN_PROXY="http://127.0.0.1:8118"` |
| **Tor Permissions** | Dropped privileges with `User tor` without explicitly fixing log/data directory ownership | Added `chown -R tor:root /var/lib/tor /var/log/tor` to prevent EACCES errors on startup |
| **Multi-Process Startup** | Single inline `CMD tor ... && privoxy ... && node server.js` lacked readiness checks | Implemented `/usr/src/app/entrypoint.sh` with socket readiness loop (`nc -z`) before launching Node |
| **Dependencies** | Missing build/runtime packages for healthchecks | Installed `bash`, `curl`, and added `package.json` with required proxy agents |

---

## 3. Usage & Build Instructions

### Build the Docker Image
```bash
docker build -t indian-proxy-cache-server .
```

### Run the Container
```bash
docker run -d \
  --name indian-proxy-server \
  -p 7890:7890 \
  -p 8118:8118 \
  -v $(pwd)/cache_segments:/usr/src/app/cache_segments \
  indian-proxy-cache-server
```

---

## 4. API Endpoints

### 1. Health Check & Geolocation Verification
* **Endpoint**: `GET /api/health?checkGeo=true`
* **Description**: Returns server status and verifies that the Tor egress IP is located in India (`IN`).
* **Example Response**:
```json
{
  "service": "Indian Tor Proxy Cache Server",
  "status": "online",
  "port": 7890,
  "proxyConfigured": "http://127.0.0.1:8118",
  "indianExitConfirmed": true,
  "proxyGeo": {
    "status": "success",
    "country": "India",
    "countryCode": "IN",
    "regionName": "National Capital Territory of Delhi",
    "city": "New Delhi",
    "isp": "Tor Exit Node"
  }
}
```

### 2. Stream Segment Proxying & Caching
* **Endpoint**: `GET /api/cache/:channelId/:segmentName`
* **Description**: Fetches HLS stream segments through the Indian Tor proxy, caches them to disk (`cache_segments/`), and serves them with `X-Cache-Status: HIT/MISS` headers.
