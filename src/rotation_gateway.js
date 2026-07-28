/**
 * Smart Rotational HTTP Proxy Gateway (Port 8888)
 * Automatically rotates outbound requests across the highest-scoring online Indian proxies in the pool.
 */

const http = require('http');
const { parseProxyAuth, executePremiumProxyFetch } = require('./premium_proxy_gateway');

const GATEWAY_PORT = process.env.GATEWAY_PORT || 8899;

const server = http.createServer(async (req, res) => {
  try {
    const targetUrl = req.url.startsWith('http') ? req.url : `http://${req.headers.host}${req.url}`;
    const authHeader = req.headers['proxy-authorization'] || req.headers['authorization'];
    const userRule = req.headers['x-proxy-user'] || '';
    const rules = parseProxyAuth(authHeader, userRule);

    const result = await executePremiumProxyFetch(targetUrl, req.method, req.headers, null, rules);

    res.setHeader('X-Indian-Proxy-ID', result.selectedProxy.id);
    res.setHeader('X-Indian-Proxy-City', result.selectedProxy.city);
    res.setHeader('X-Indian-Proxy-ISP', result.selectedProxy.isp);
    res.setHeader('X-Indian-Proxy-Type', result.selectedProxy.type);
    res.setHeader('X-Indian-Proxy-Score', result.selectedProxy.score);
    res.setHeader('X-Indian-Proxy-Rules-Applied', JSON.stringify(result.rulesApplied));
    res.writeHead(result.status, result.headers);
    res.end(typeof result.data === 'object' ? JSON.stringify(result.data) : result.data);
  } catch (err) {
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      error: 'Smart rotation gateway fetch error',
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
  startGateway
};
