FROM node:20-alpine

# Set node environment to production
ENV NODE_ENV=production

# Pre-configure our automatic free Indian Residential/Exit proxy (Tor SOCKS5 -> Privoxy HTTP)
ENV INDIAN_PROXY="http://127.0.0.1:8118"

# Install Tor, Privoxy, bash, and curl (for health checking)
RUN apk add --no-cache tor privoxy bash curl

# Create app directory
WORKDIR /usr/src/app

# Copy package and configuration files
COPY package*.json ./
COPY allowed_247_channels.json ./

# Install Node.js dependencies
RUN npm install --omit=dev || true

# Copy all application source directories and files
COPY src/ ./src/
COPY public/ ./public/
COPY server.js* ./
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Configure Tor (Enforce SOCKS5 on 9050, route only through Indian Exit Nodes)
RUN mkdir -p /var/lib/tor && \
    chown -R tor:root /var/lib/tor && \
    chmod -R 700 /var/lib/tor && \
    echo "ExitNodes {in}" >> /etc/tor/torrc && \
    echo "StrictNodes 1" >> /etc/tor/torrc && \
    echo "SocksPort 0.0.0.0:9050" >> /etc/tor/torrc && \
    echo "DataDirectory /var/lib/tor" >> /etc/tor/torrc && \
    echo "User tor" >> /etc/tor/torrc && \
    echo "Log notice file /var/log/tor/notices.log" >> /etc/tor/torrc && \
    mkdir -p /var/log/tor && \
    chown -R tor:root /var/log/tor

# Configure Privoxy (Convert SOCKS5 Tor proxy to standard HTTP Proxy on Port 8118)
RUN echo "forward-socks5t / 127.0.0.1:9050 ." >> /etc/privoxy/config && \
    echo "listen-address 0.0.0.0:8118" >> /etc/privoxy/config && \
    sed -i 's/toggle 1/toggle 0/g' /etc/privoxy/config || true

# Create cache directory and grant permissions
RUN mkdir -p cache_segments && chmod -R 777 cache_segments

# Expose HTTP API Server (8000), Smart Gateway (8899), Stream Cache (7890), Privoxy (8118), Tor SOCKS5 (9050)
EXPOSE 8000 8899 7890 8118 9050

# Use custom entrypoint script to cleanly start Tor, Privoxy, and Node.js
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
