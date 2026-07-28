/**
 * 24/7 Indian Channel Caching & Proxy Server
 * Routes outbound channel segment fetches through an Indian residential/exit node
 * using Privoxy (http://127.0.0.1:8118) -> Tor SOCKS5 (127.0.0.1:9050).
 */

const fs = require('fs');
const path = require('path');
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const axios = require('axios');
const { HttpProxyAgent } = require('http-proxy-agent');
const { HttpsProxyAgent } = require('https-proxy-agent');

const PORT = process.env.PORT || 7890;
const INDIAN_PROXY_URL = process.env.INDIAN_PROXY || 'http://127.0.0.1:8118';
const CACHE_DIR = path.resolve(__dirname, 'cache_segments');

// Ensure cache directory exists
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

// Load channel configuration
let allowedChannelsConfig = { channels: [], cacheSettings: {} };
try {
  const configPath = path.resolve(__dirname, 'allowed_247_channels.json');
  if (fs.existsSync(configPath)) {
    allowedChannelsConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  }
} catch (err) {
  console.error('[Server] Failed to load allowed_247_channels.json:', err.message);
}

// Create proxy agents for outbound requests
const httpAgent = new HttpProxyAgent(INDIAN_PROXY_URL);
const httpsAgent = new HttpsProxyAgent(INDIAN_PROXY_URL);

const axiosProxyClient = axios.create({
  httpAgent,
  httpsAgent,
  timeout: 15000,
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  }
});

const app = express();
app.use(cors());
app.use(morgan('dev'));

/**
 * Health check & Indian Proxy Geolocation Verification Endpoint
 */
app.get('/api/health', async (req, res) => {
  const status = {
    service: 'Indian Tor Proxy Cache Server',
    status: 'online',
    port: PORT,
    proxyConfigured: INDIAN_PROXY_URL,
    cacheDirectory: CACHE_DIR,
    channelsCount: allowedChannelsConfig.channels.length,
    timestamp: new Date().toISOString()
  };

  // Optionally check proxy IP geo-location
  if (req.query.checkGeo === 'true') {
    try {
      const geoRes = await axiosProxyClient.get('http://ip-api.com/json/?fields=status,country,countryCode,regionName,city,isp,query');
      status.proxyGeo = geoRes.data;
      status.indianExitConfirmed = (geoRes.data && geoRes.data.countryCode === 'IN');
    } catch (err) {
      status.proxyGeoError = err.message;
      status.indianExitConfirmed = false;
    }
  }

  res.json(status);
});

/**
 * List allowed 24/7 channels
 */
app.get('/api/channels', (req, res) => {
  res.json({
    success: true,
    channels: allowedChannelsConfig.channels
  });
});

/**
 * Proxy and cache a segment file
 */
app.get('/api/cache/:channelId/:segmentName', async (req, res) => {
  const { channelId, segmentName } = req.params;
  const channel = allowedChannelsConfig.channels.find(c => c.id === channelId);

  if (!channel) {
    return res.status(404).json({ error: 'Channel not found in allowed_247_channels.json' });
  }

  const sanitizedSegment = segmentName.replace(/[^a-zA-Z0-9_.-]/g, '');
  const cachePath = path.join(CACHE_DIR, `${channelId}_${sanitizedSegment}`);

  // Serve from cache if existing
  if (fs.existsSync(cachePath)) {
    res.setHeader('X-Cache-Status', 'HIT');
    return res.sendFile(cachePath);
  }

  // Fetch through Indian Tor Proxy and cache
  try {
    const segmentUrl = new URL(sanitizedSegment, channel.streamUrl).toString();
    const response = await axiosProxyClient.get(segmentUrl, { responseType: 'stream' });

    const writer = fs.createWriteStream(cachePath);
    response.data.pipe(writer);

    writer.on('finish', () => {
      res.setHeader('X-Cache-Status', 'MISS');
      res.sendFile(cachePath);
    });

    writer.on('error', (err) => {
      console.error('[Server] File cache write error:', err.message);
      res.status(500).json({ error: 'Failed to write cache segment' });
    });
  } catch (err) {
    console.error(`[Server] Proxy fetch error for ${channelId}/${segmentName}:`, err.message);
    res.status(502).json({
      error: 'Proxy stream fetch failed',
      details: err.message,
      proxy: INDIAN_PROXY_URL
    });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log('='.repeat(80));
  console.log(`[Server] 24/7 Channel Caching Server running on port ${PORT}`);
  console.log(`[Server] Indian Proxy Gateway: ${INDIAN_PROXY_URL} (Privoxy -> Tor SOCKS5 9050)`);
  console.log(`[Server] Segment Cache Dir:   ${CACHE_DIR}`);
  console.log('='.repeat(80));
});
