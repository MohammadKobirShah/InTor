/**
 * Smart Rotational HTTP Proxy Gateway (Port 8888)
 * Automatically rotates outbound requests across the highest-scoring online Indian proxies in the pool.
 */

const http = require('http');
const { loadPool } = require('./checker_engine');
const { HttpProxyAgent } = require('http-proxy-agent');
const { SocksProxyAgent } = require('socks-proxy-agent');
const axios = require('axios');

const GATEWAY_PORT = process.env.GATEWAY_PORT || 8899;

function getBestIndianProxy(filters = {}) {
  const data = loadPool();
  const onlineProxies = data.pool.filter(p => {
    if (p.status !== 'online' || p.countryCode !== 'IN') return false;
    if (filters.city && p.city.toLowerCase() !== filters.city.toLowerCase()) return false;
    if (filters.isp && !p.isp.toLowerCase().includes(filters.isp.toLowerCase())) return false;
    if (filters.minScore && p.score < filters.minScore) return false;
    return true;
  });

  if (onlineProxies.length === 0) return null;

  // Weighted random selection biased towards highest quality score
  onlineProxies.sort((a, b) => b.score - a.score);
  // Pick from the top 3 to distribute load while maintaining speed
  const topCandidateCount = Math.min(3, onlineProxies.length);
  const randomIndex = Math.floor(Math.random() * topCandidateCount);
  return onlineProxies[randomIndex];
}

const server = http.createServer(async (req, res) => {
  const selectedProxy = getBestIndianProxy();

  if (!selectedProxy) {
    res.writeHead(503, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ error: 'No online Indian proxies available in the pool' }));
  }

  res.setHeader('X-Indian-Proxy-ID', selectedProxy.id);
  res.setHeader('X-Indian-Proxy-City', selectedProxy.city);
  res.setHeader('X-Indian-Proxy-ISP', selectedProxy.isp);
  res.setHeader('X-Indian-Proxy-Score', selectedProxy.score);

  try {
    const targetUrl = req.url.startsWith('http') ? req.url : `http://${req.headers.host}${req.url}`;
    const isSocks = selectedProxy.url.toLowerCase().startsWith('socks') || (selectedProxy.protocol && selectedProxy.protocol.toLowerCase().includes('socks'));
    const agent = isSocks ? new SocksProxyAgent(selectedProxy.url) : new HttpProxyAgent(selectedProxy.url);

    const proxyRes = await axios({
      method: req.method,
      url: targetUrl,
      headers: { ...req.headers, host: undefined },
      httpAgent: agent,
      validateStatus: () => true
    });

    res.writeHead(proxyRes.status, proxyRes.headers);
    res.end(proxyRes.data);
  } catch (err) {
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      error: 'Smart rotation gateway fetch error',
      proxyUsed: selectedProxy.id,
      details: err.message
    }));
  }
});

function startGateway() {
  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.warn(`[Rotation Gateway] Port ${GATEWAY_PORT} is already in use. Using existing gateway instance.`);
    } else {
      console.error('[Rotation Gateway] Error:', err.message);
    }
  });

  server.listen(GATEWAY_PORT, '0.0.0.0', () => {
    console.log(`[Rotation Gateway] Smart Indian Proxy Gateway listening on port ${GATEWAY_PORT}`);
  });
}

if (require.main === module) {
  startGateway();
}

module.exports = {
  getBestIndianProxy,
  startGateway
};
