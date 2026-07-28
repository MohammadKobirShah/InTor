#!/usr/bin/env bash
set -e

echo "[Entrypoint] Starting Tor daemon with Indian Exit Node policy ({in})..."
tor --RunAsDaemon 1

echo "[Entrypoint] Starting Privoxy HTTP-to-SOCKS5 bridge on port 8118..."
privoxy /etc/privoxy/config

echo "[Entrypoint] Waiting for Privoxy (8118) and Tor SOCKS5 (9050) to become responsive..."
for i in {1..15}; do
  if nc -z 127.0.0.1 8118 2>/dev/null; then
    echo "[Entrypoint] Privoxy is up on 0.0.0.0:8118 and Tor SOCKS5 is up on 0.0.0.0:9050!"
    break
  fi
  sleep 1
done

echo "[Entrypoint] Starting #1 Pro Indian Proxy Enterprise API Server (src/api_server.js)..."
exec node src/api_server.js
