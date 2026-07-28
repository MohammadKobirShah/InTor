/**
 * Enterprise Indian Proxy REST API & Dashboard Server (#1 Pro-Grade Suite)
 * Serves JSON APIs for smart proxy selection, real-time health checks, and dashboard analytics.
 * Includes Premium Rotating Proxy Gateway (#1 BrightData / Oxylabs Pro-Level Architecture).
 */

const fs = require('fs');
const path = require('path');
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const { loadPool, savePool, runPoolSweep, startAutoPoolUpdater } = require('./checker_engine');
const { getBestIndianProxy, startGateway } = require('./rotation_gateway');
const { parseProxyAuth, selectPremiumProxy, executePremiumProxyFetch } = require('./premium_proxy_gateway');

const API_PORT = process.env.PORT || process.env.API_PORT || 8000;

const app = express();
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

/**
 * #1 UPGRADE: Single-Port Transparent Premium HTTP Proxy Middleware
 * Supports BrightData/Oxylabs style Proxy-Authorization username rules!
 * Example: curl -x http://user-in-type-tor:pass@intor2.onrender.com "http://ip-api.com/json/"
 */
app.use(async (req, res, next) => {
  if (req.url.startsWith('http://') || req.url.startsWith('https://')) {
    try {
      const authHeader = req.headers['proxy-authorization'] || req.headers['authorization'];
      const userRule = req.headers['x-proxy-user'] || '';
      const rules = parseProxyAuth(authHeader, userRule);

      const result = await executePremiumProxyFetch(req.url, req.method, req.headers, req.body, rules);
      res.setHeader('X-Indian-Proxy-ID', result.selectedProxy.id);
      res.setHeader('X-Indian-Proxy-City', result.selectedProxy.city);
      res.setHeader('X-Indian-Proxy-ISP', result.selectedProxy.isp);
      res.setHeader('X-Indian-Proxy-Type', result.selectedProxy.type);
      res.setHeader('X-Indian-Proxy-Score', result.selectedProxy.score);
      res.setHeader('X-Indian-Proxy-Rules-Applied', JSON.stringify(result.rulesApplied));
      res.status(result.status).send(result.data);
    } catch (err) {
      res.status(502).json({
        success: false,
        error: 'Single-Port Transparent Premium Proxy Gateway fetch failed',
        details: err.message
      });
    }
  } else {
    next();
  }
});

// Serve Web Admin Dashboard static files
app.use(express.static(path.resolve(__dirname, '../public')));

/**
 * Helper to filter pool based on request query params
 */
function applyFilters(pool, query) {
  const { status, city, isp, type, protocol, minScore, limit, sortBy } = query;

  const statusFilter = status || 'online';
  if (statusFilter.toLowerCase() !== 'all') {
    pool = pool.filter(p => p.status.toLowerCase() === statusFilter.toLowerCase());
  }

  if (type) {
    pool = pool.filter(p => p.type && p.type.toLowerCase() === type.toLowerCase());
  }
  if (protocol) {
    pool = pool.filter(p => p.protocol.toLowerCase() === protocol.toLowerCase() || p.url.toLowerCase().startsWith(protocol.toLowerCase()));
  }
  if (city) {
    pool = pool.filter(p => p.city.toLowerCase().includes(city.toLowerCase()));
  }
  if (isp) {
    pool = pool.filter(p => p.isp.toLowerCase().includes(isp.toLowerCase()));
  }
  if (minScore) {
    pool = pool.filter(p => p.score >= parseInt(minScore, 10));
  }

  if (sortBy === 'latency') {
    pool.sort((a, b) => (a.latencyMs || 9999) - (b.latencyMs || 9999));
  } else {
    pool.sort((a, b) => (b.score || 0) - (a.score || 0));
  }

  if (limit) {
    pool = pool.slice(0, parseInt(limit, 10));
  }
  return pool;
}

/**
 * #1 UPGRADE: Premium BrightData / Oxylabs Style Rotating Gateway Endpoint
 * GET /api/v1/rotate?url=http://ip-api.com/json/&type=tor&city=mumbai
 * Works 100% on Render.com & Railway over standard HTTP/HTTPS!
 */
app.all('/api/v1/rotate', async (req, res) => {
  const targetUrl = req.query.url || req.headers['x-target-url'] || (req.body && req.body.url);
  if (!targetUrl || (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://'))) {
    return res.status(400).json({
      success: false,
      error: 'Provide a valid target URL starting with http:// or https://',
      example: '/api/v1/rotate?url=http://ip-api.com/json/&type=tor'
    });
  }

  try {
    const rules = {
      type: req.query.type || (req.body && req.body.type) || null,
      city: req.query.city || (req.body && req.body.city) || null,
      isp: req.query.isp || (req.body && req.body.isp) || null,
      session: req.query.session || (req.body && req.body.session) || null,
      protocol: req.query.protocol || (req.body && req.body.protocol) || null
    };

    const result = await executePremiumProxyFetch(targetUrl, req.method, req.headers, req.body, rules);
    res.setHeader('X-Indian-Proxy-ID', result.selectedProxy.id);
    res.setHeader('X-Indian-Proxy-City', result.selectedProxy.city);
    res.setHeader('X-Indian-Proxy-ISP', result.selectedProxy.isp);
    res.setHeader('X-Indian-Proxy-Type', result.selectedProxy.type);
    res.setHeader('X-Indian-Proxy-Score', result.selectedProxy.score);
    res.setHeader('X-Indian-Proxy-Tor-Status', result.torStatus || 'N/A');
    res.setHeader('X-Indian-Proxy-Rules-Applied', JSON.stringify(result.rulesApplied));
    res.status(result.status).send(result.data);
  } catch (err) {
    res.status(502).json({
      success: false,
      error: 'Premium Rotating Proxy Gateway fetch failed',
      details: err.message
    });
  }
});

/**
 * Backward-compatible /api/v1/fetch endpoint
 */
app.all('/api/v1/fetch', async (req, res) => {
  const targetUrl = req.query.url || req.headers['x-target-url'] || (req.body && req.body.url);
  if (!targetUrl || (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://'))) {
    return res.status(400).json({
      success: false,
      error: 'Provide a valid target URL starting with http:// or https://',
      example: '/api/v1/fetch?url=http://ip-api.com/json/'
    });
  }

  try {
    const result = await executePremiumProxyFetch(targetUrl, req.method, req.headers, req.body);
    res.setHeader('X-Indian-Proxy-ID', result.selectedProxy.id);
    res.setHeader('X-Indian-Proxy-City', result.selectedProxy.city);
    res.setHeader('X-Indian-Proxy-ISP', result.selectedProxy.isp);
    res.setHeader('X-Indian-Proxy-Score', result.selectedProxy.score);
    res.status(result.status).send(result.data);
  } catch (err) {
    res.status(502).json({
      success: false,
      error: 'REST Indian Proxy Gateway fetch failed',
      details: err.message
    });
  }
});

/**
 * 1. Primary Filterable List Endpoint
 * GET /api/v1/proxies?type=mobile&status=online&city=Mumbai&minScore=90
 */
app.get('/api/v1/proxies', (req, res) => {
  const data = loadPool();
  const pool = applyFilters(data.pool, req.query);

  res.json({
    success: true,
    count: pool.length,
    updatedAt: data.updatedAt,
    proxies: pool
  });
});

/**
 * 2. PRO ROUTE: Only Residential (FTTH/Broadband) Indian Proxies
 * GET /api/v1/proxies/residential
 */
app.get('/api/v1/proxies/residential', (req, res) => {
  const data = loadPool();
  let pool = data.pool.filter(p => p.type === 'residential' || p.residential === true);
  pool = applyFilters(pool, req.query);

  res.json({
    success: true,
    category: 'Residential (FTTH & Broadband)',
    count: pool.length,
    proxies: pool
  });
});

/**
 * 3. PRO ROUTE: Only Mobile 4G/5G Cellular Indian Proxies
 * GET /api/v1/proxies/mobile
 */
app.get('/api/v1/proxies/mobile', (req, res) => {
  const data = loadPool();
  let pool = data.pool.filter(p => p.type === 'mobile' || p.mobile === true);
  pool = applyFilters(pool, req.query);

  res.json({
    success: true,
    category: 'Mobile Cellular (4G/5G Carrier)',
    count: pool.length,
    proxies: pool
  });
});

/**
 * 4. PRO ROUTE: Only Datacenter Indian Proxies
 * GET /api/v1/proxies/datacenter
 */
app.get('/api/v1/proxies/datacenter', (req, res) => {
  const data = loadPool();
  let pool = data.pool.filter(p => p.type === 'datacenter');
  pool = applyFilters(pool, req.query);

  res.json({
    success: true,
    category: 'Datacenter / Cloud Hosting',
    count: pool.length,
    proxies: pool
  });
});

/**
 * 5. PRO ROUTE: Only Tor Indian Exit Node Proxies
 * GET /api/v1/proxies/tor
 */
app.get('/api/v1/proxies/tor', (req, res) => {
  const data = loadPool();
  let pool = data.pool.filter(p => p.type === 'tor');
  pool = applyFilters(pool, req.query);

  res.json({
    success: true,
    category: 'Tor Indian Exit Nodes',
    count: pool.length,
    proxies: pool
  });
});

/**
 * 6. PRO ROUTE: Custom ISP Filter Route
 * GET /api/v1/proxies/isp/:ispName
 */
app.get('/api/v1/proxies/isp/:ispName', (req, res) => {
  const ispName = req.params.ispName.toLowerCase();
  const data = loadPool();
  let pool = data.pool.filter(p => p.isp.toLowerCase().includes(ispName));
  pool = applyFilters(pool, req.query);

  res.json({
    success: true,
    ispQuery: req.params.ispName,
    count: pool.length,
    proxies: pool
  });
});

/**
 * 7. PRO ROUTE: Plain-Text Export for Scrapers, Bots & Tools
 * GET /api/v1/proxies/export?format=txt&type=mobile&protocol=socks5
 */
app.get('/api/v1/proxies/export', (req, res) => {
  const data = loadPool();
  const pool = applyFilters(data.pool, req.query);

  if (req.query.format === 'json') {
    return res.json(pool.map(p => p.url));
  }

  res.setHeader('Content-Type', 'text/plain');
  res.setHeader('Content-Disposition', 'inline; filename="indian_proxies.txt"');
  const textList = pool.map(p => p.url).join('\n');
  res.send(textList);
});

/**
 * 8. Get a Single Random High-Scoring Indian Proxy
 * GET /api/v1/proxies/random?city=Mumbai&type=mobile
 */
app.get('/api/v1/proxies/random', (req, res) => {
  const selected = selectPremiumProxy(req.query);

  res.json({
    success: true,
    proxy: selected
  });
});

/**
 * 9. Get Comprehensive Pool Analytics & Type Breakdown
 * GET /api/v1/stats
 */
app.get('/api/v1/stats', (req, res) => {
  const data = loadPool();
  const pool = data.pool;

  const online = pool.filter(p => p.status === 'online');
  const totalLatency = online.reduce((sum, p) => sum + (p.latencyMs || 0), 0);
  const avgLatencyMs = online.length > 0 ? Math.round(totalLatency / online.length) : 0;

  const byCity = {};
  const byISP = {};
  const byType = { residential: 0, mobile: 0, datacenter: 0, tor: 0 };

  online.forEach(p => {
    byCity[p.city] = (byCity[p.city] || 0) + 1;
    const shortISP = p.isp.split(' ')[0];
    byISP[shortISP] = (byISP[shortISP] || 0) + 1;
    if (p.type && byType[p.type] !== undefined) {
      byType[p.type]++;
    }
  });

  res.json({
    success: true,
    analytics: {
      totalPoolSize: pool.length,
      onlineCount: online.length,
      offlineCount: pool.length - online.length,
      averageLatencyMs: avgLatencyMs,
      averageQualityScore: online.length > 0 ? Math.round(online.reduce((s, p) => s + p.score, 0) / online.length) : 0,
      typeDistribution: byType,
      citiesDistribution: byCity,
      ispDistribution: byISP,
      lastSweepAt: data.updatedAt
    }
  });
});

/**
 * 10. Trigger Real-Time Health Verification Sweep
 * POST /api/v1/proxies/check
 */
app.post('/api/v1/proxies/check', async (req, res) => {
  try {
    const result = await runPoolSweep();
    res.json({
      success: true,
      message: 'Pool sweep completed and scores updated',
      updatedAt: result.updatedAt,
      onlineCount: result.pool.filter(p => p.status === 'online').length
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * 11. Add Custom Indian Proxies Dynamically
 * POST /api/v1/proxies/add
 */
app.post('/api/v1/proxies/add', (req, res) => {
  const { proxies } = req.body;
  if (!Array.isArray(proxies) || proxies.length === 0) {
    return res.status(400).json({ success: false, error: 'Provide a valid "proxies" array in body' });
  }

  const data = loadPool();
  let addedCount = 0;

  proxies.forEach((url, index) => {
    const exists = data.pool.some(p => p.url === url);
    if (!exists) {
      data.pool.push({
        id: `custom-in-${Date.now()}-${index}`,
        url: url,
        protocol: url.toLowerCase().startsWith('socks') ? 'socks5' : 'http',
        type: 'residential',
        residential: true,
        mobile: false,
        countryCode: 'IN',
        country: 'India',
        state: 'Pending Verification',
        city: 'Unknown',
        zip: '110001',
        lat: 20.5937,
        lon: 78.9629,
        isp: 'Custom Indian Proxy',
        org: 'Custom Network',
        asn: 'AS0000',
        anonymity: 'Pending',
        latencyMs: 180,
        downloadMbps: 20,
        score: 85,
        status: 'online',
        lastChecked: new Date().toISOString()
      });
      addedCount++;
    }
  });

  if (addedCount > 0) {
    savePool(data);
  }

  res.json({
    success: true,
    addedCount,
    totalPoolSize: data.pool.length
  });
});

app.listen(API_PORT, '0.0.0.0', () => {
  console.log('='.repeat(80));
  console.log(`[API Server] #1 Indian Proxy Enterprise API Server running on port ${API_PORT}`);
  console.log(`[API Server] REST API Base:                      http://localhost:${API_PORT}/api/v1/proxies`);
  console.log(`[API Server] Premium Rotating Gateway Endpoint:  http://localhost:${API_PORT}/api/v1/rotate?type=tor`);
  console.log(`[API Server] BrightData Style Proxy Auth:        curl -x http://user-in-type-tor:pass@localhost:${API_PORT} ...`);
  console.log('='.repeat(80));
});

// Automatically launch standalone Rotation Gateway on port 8899 if possible
startGateway();

// Automatically sweep and harvest live Indian proxies every 60 seconds (1 minute)
startAutoPoolUpdater(60000);
