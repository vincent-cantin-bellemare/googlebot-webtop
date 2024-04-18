# Install dependencies

apt-get update && apt-get install -y \
    python3-pip \
    wget \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

wget -q -O /tmp/tor-browser-linux64.tar.xz "https://www.torproject.org/dist/torbrowser/13.0.14/tor-browser-linux-x86_64-13.0.14.tar.xz" && \
    mkdir -p /opt/tor-browser && \
    tar -xf /tmp/tor-browser-linux64.tar.xz -C /opt/tor-browser --strip-components=1 && \
    rm /tmp/tor-browser-linux64.tar.xz

echo '/opt/tor-browser/Browser/start-tor-browser --detach --marionette || echo "Tor Browser failed to start"' > /usr/local/bin/start-tor-browser
chmod +x /usr/local/bin/start-tor-browser
chown -R 5001:5001 /opt/tor-browser

pip3 install -r /app/requirements.txt
