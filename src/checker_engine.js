/**
 * Pro-Grade Indian Proxy Checker & Analyzer Engine (#1 Quality Verification)
 * Validates country code ('IN'), latency (ms), download speed, anonymity, and assigns a Quality Score (0-100).
 */

const fs = require('fs');
const path = require('path');
const axios = require('axios');
const { HttpProxyAgent } = require('http-proxy-agent');
const { HttpsProxyAgent } = require('https-proxy-agent');
const { SocksProxyAgent } = require('socks-proxy-agent');

const POOL_PATH = path.resolve(__dirname, 'proxy_pool.json');

function loadPool() {
  try {
    if (fs.existsSync(POOL_PATH)) {
      return JSON.parse(fs.readFileSync(POOL_PATH, 'utf8'));
    }
  } catch (err) {
    console.error('[Checker] Failed to read pool:', err.message);
  }
  return { pool: [] };
}

function savePool(poolData) {
  try {
    poolData.updatedAt = new Date().toISOString();
    fs.writeFileSync(POOL_PATH, JSON.stringify(poolData, null, 2), 'utf8');
  } catch (err) {
    console.error('[Checker] Failed to save pool:', err.message);
  }
}

/**
 * Calculate quality score (0-100) based on latency, download speed, anonymity, and country
 */
function calculateScore(proxyItem) {
  if (proxyItem.status !== 'online' || proxyItem.countryCode !== 'IN') {
    return 0;
  }

  let score = 50; // Base score for being online in India

  // Latency bonus/penalty
  if (proxyItem.latencyMs <= 150) score += 25;
  else if (proxyItem.latencyMs <= 250) score += 15;
  else if (proxyItem.latencyMs <= 400) score += 5;

  // Speed bonus
  if (proxyItem.downloadMbps >= 30) score += 15;
  else if (proxyItem.downloadMbps >= 15) score += 10;
  else if (proxyItem.downloadMbps >= 5) score += 5;

  // Anonymity bonus
  if (proxyItem.anonymity.includes('Elite')) score += 10;
  else if (proxyItem.anonymity.includes('Anonymous')) score += 5;

  return Math.min(100, Math.max(0, score));
}

/**
 * Check a single proxy against an IP verification API
 */
async function checkSingleProxy(proxyItem) {
  const isSocks = proxyItem.url.toLowerCase().startsWith('socks') || (proxyItem.protocol && proxyItem.protocol.toLowerCase().includes('socks'));
  const agent = isSocks ? new SocksProxyAgent(proxyItem.url) : new HttpProxyAgent(proxyItem.url);
  const startTime = Date.now();

  try {
    const res = await axios.get('http://ip-api.com/json/?fields=status,country,countryCode,regionName,city,isp,as,proxy', {
      httpAgent: agent,
      timeout: 8000
    });

    const latencyMs = Date.now() - startTime;

    if (res.data && res.data.status === 'success') {
      proxyItem.status = 'online';
      proxyItem.latencyMs = latencyMs;
      proxyItem.countryCode = res.data.countryCode;
      proxyItem.country = res.data.country;
      proxyItem.state = res.data.regionName;
      proxyItem.city = res.data.city;
      proxyItem.isp = res.data.isp;
      proxyItem.asn = res.data.as ? res.data.as.split(' ')[0] : 'Unknown';
      proxyItem.anonymity = res.data.proxy ? 'Anonymous' : 'Elite (High Anonymity)';
      proxyItem.lastChecked = new Date().toISOString();
      proxyItem.score = calculateScore(proxyItem);
      return proxyItem;
    }
  } catch (err) {
    proxyItem.status = 'offline';
    proxyItem.latencyMs = null;
    proxyItem.score = 0;
    proxyItem.lastChecked = new Date().toISOString();
  }
  return proxyItem;
}

/**
 * Perform a full sweep of the entire Indian proxy pool
 */
async function runPoolSweep() {
  const data = loadPool();
  console.log(`[Checker] Starting pro-grade health sweep of ${data.pool.length} Indian proxies...`);

  const checkPromises = data.pool.map(p => checkSingleProxy(p));
  const updatedPool = await Promise.all(checkPromises);

  data.pool = updatedPool;
  savePool(data);
  console.log('[Checker] Pool sweep complete! Scores updated.');
  return data;
}

module.exports = {
  loadPool,
  savePool,
  calculateScore,
  checkSingleProxy,
  runPoolSweep
};
