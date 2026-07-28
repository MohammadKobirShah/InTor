# 🇮🇳 #1 Premium & Pro-Grade Indian Proxy Platform, REST API & Multi-Server Suite

> **আপনার টার্গেট #1 করা! (Mobile 4G/5G, Residential FTTH, Custom ISP & SOCKS5/HTTP সাপোর্টেড!)**  
> এই কমপ্লিট এন্টারপ্রাইজ আর্কিটেকচারে আপনি পাচ্ছেন **Mobile 4G/5G Cellular**, **Residential FTTH/Broadband**, **Datacenter** এবং **Tor Exit Nodes**-এর আলাদা আলাদা ডেডিকেটেড **Pro API Routes**, **SOCKS5/HTTP প্রোটোকল সাপোর্ট**, **Smart Rotational Gateway (`:8899`)**, এবং একটি **Dark-Mode Web Admin Dashboard (`:8000`)**।

---

## 🌟 নতুন Pro API Routes (Mobile, Residential & Custom ISP)

আপনার প্রজেক্টটিকে মার্কেট লিডার **(#1 Pro-Grade Platform)** করার জন্য আমরা নিচের ডেডিকেটেড API রাউটগুলো তৈরি করেছি:

```
+---------------------------------------------------------------------------------------------------+
|  ENTERPRISE PRO API ROUTES (Base URL: http://localhost:8000/api/v1)                               |
+---------------------------------------------------------------------------------------------------+
|  1. GET  /proxies/residential       |  শুধুমাত্র Residential FTTH/Broadband (JioFiber, Airtel)    |
|  2. GET  /proxies/mobile            |  শুধুমাত্র 4G/5G Mobile Carrier (Jio 5G, Airtel 4G, Vi)     |
|  3. GET  /proxies/datacenter        |  শুধুমাত্র Datacenter / Cloud Hosting (Tata, Sify)          |
|  4. GET  /proxies/tor               |  শুধুমাত্র Tor Indian Exit Nodes (High Anonymity)           |
|  5. GET  /proxies/isp/:ispName      |  নির্দিষ্ট ISP ফিল্টার (যেমন: /isp/jio বা /isp/airtel)       |
|  6. GET  /proxies/export            |  সরাসরি .TXT বা JSON ফরম্যাটে এক্সপোর্ট (Scraper/Bot Ready) |
|  7. GET  /proxies/random            |  যেকোনো ক্যাটাগরির রেন্ডম হাই-স্পিড প্রক্সি                   |
|  8. GET  /stats                     |  পুল অ্যানালিটিক্স এবং টাইপ ডিস্ট্রিবিউশন                     |
|  9. POST /proxies/check             |  রিয়েল-টাইম হেলথ ও স্পিড ভেরিফিকেশন সুইপ                    |
| 10. POST /proxies/add               |  নতুন কাস্টম প্রক্সি লিস্ট অ্যাড করা                          |
+---------------------------------------------------------------------------------------------------+
```

---

## 1. Pro API Route Examples & Usage (বাংলায় সহজ গাইড)

### ১. শুধুমাত্র Residential (FTTH / Broadband) প্রক্সি লিস্ট
বাসাবাড়ির ব্রডব্যান্ড (JioFiber, Airtel Xstream, ACT Fibernet, BSNL)-এর প্রক্সি নিতে:
```bash
curl "http://localhost:8000/api/v1/proxies/residential?city=Mumbai&minScore=90"
```

### ২. শুধুমাত্র Mobile 4G/5G Cellular প্রক্সি লিস্ট
মোবাইল আইপি (Reliance Jio 5G, Airtel 4G LTE, Vi Mobile)—যা সোশ্যাল মিডিয়া ও ই-কমার্স স্ক্র্যাপিংয়ে কখনো ব্লক হয় না:
```bash
curl "http://localhost:8000/api/v1/proxies/mobile?isp=Jio&protocol=socks5"
```

### ৩. কাস্টম ISP ফিল্টার Route (`/api/v1/proxies/isp/:ispName`)
আপনি চাইলে যেকোনো নির্দিষ্ট কোম্পানির আইপি এক ক্লিকেই নিতে পারবেন:
```bash
# শুধুমাত্র Reliance Jio-এর সব প্রক্সি (Mobile + Residential)
curl "http://localhost:8000/api/v1/proxies/isp/jio"

# শুধুমাত্র Bharti Airtel-এর সব প্রক্সি
curl "http://localhost:8000/api/v1/proxies/isp/airtel"

# শুধুমাত্র BSNL বা ACT Fibernet-এর প্রক্সি
curl "http://localhost:8000/api/v1/proxies/isp/bsnl"
curl "http://localhost:8000/api/v1/proxies/isp/act"
```

### ৪. Scraper ও Bot-এর জন্য সরাসরি `.TXT` ফরম্যাটে Export
আপনার পাইথন স্ক্র্যাপার বা বটের জন্য কোনো JSON পার্স না করেই সরাসরি `ip:port` বা `socks5://ip:port` লিস্ট পেতে:
```bash
# সব 4G/5G Mobile SOCKS5 প্রক্সি .txt ফরম্যাটে এক্সপোর্ট
curl "http://localhost:8000/api/v1/proxies/export?format=txt&type=mobile&protocol=socks5"

# সব Residential প্রক্সি .txt ফরম্যাটে এক্সপোর্ট
curl "http://localhost:8000/api/v1/proxies/export?format=txt&type=residential"
```

---

## 2. Smart Rotational Gateway (`:8888`) Integration Guides

আপনার স্ক্র্যাপারে বারবার প্রক্সি চেঞ্জ করার ঝামেলা না রেখে সরাসরি **`http://localhost:8888`** ব্যবহার করুন। আমাদের রোটিং গেটওয়ে স্বয়ংক্রিয়ভাবে সেরা কোয়ালিটি স্কোরের ইন্ডিয়ান প্রক্সির মাধ্যমে রিকোয়েস্ট পাঠাবে!

### Python (Requests / Scrapy)
```python
import requests

proxy_url = "http://localhost:8888"
proxies = {
    "http": proxy_url,
    "https": proxy_url
}

# Every call automatically routes through a top-rated Indian proxy
response = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=10)
data = response.json()
print("Rotated Indian IP:", data.get("query"))
print("City:", data.get("city"), "| ISP:", data.get("isp"))
```

### Node.js (Axios / Puppeteer / Playwright)
```javascript
const axios = require('axios');
const { HttpProxyAgent } = require('http-proxy-agent');

const agent = new HttpProxyAgent('http://localhost:8888');

async function runScraper() {
  const res = await axios.get('http://ip-api.com/json/', { httpAgent: agent });
  console.log('Rotated Indian Exit IP:', res.data.query);
  console.log('ISP:', res.data.isp, '| City:', res.data.city);
}

runScraper();
```

---

## 3. How to Launch & Scale (#1 Pro Roadmap)

### 1. Launch with Node directly
```bash
# Start the Pro API Server & Admin Dashboard (port 8000) + Smart Gateway (port 8888)
node src/api_server.js
```

### 2. Launch Complete Multi-Server Cluster with Docker Compose
```bash
docker-compose -f docker-compose.pro.yml up -d --build
```
* **REST API & Dashboard**: `http://localhost:8000/`
* **Smart Rotation Gateway**: `http://localhost:8888/`
* **Tor SOCKS5 Ports**: `127.0.0.1:9050`, `9051`, `9052`
* **Tor Privoxy Ports**: `127.0.0.1:8118`, `8119`, `8120`
