FROM lscr.io/linuxserver/webtop:ubuntu-mate


RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get install -y python3.11 python3.11-venv python3.11-distutils python3.11-dev \
    && apt-get install -y firefox \
    && apt-get install -y nano \
    && rm -rf /var/lib/apt/lists/*


RUN apt-get update && apt-get install -y \
    python3-pip \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

COPY tor/tor-browser-linux64.tar.xz /tmp/tor-browser-linux64.tar.xz
RUN mkdir -p /opt/tor-browser && \
    tar -xf /tmp/tor-browser-linux64.tar.xz -C /opt/tor-browser --strip-components=1 && \
    rm /tmp/tor-browser-linux64.tar.xz && \
    echo '#!/bin/bash\n/opt/tor-browser/Browser/start-tor-browser --detach --marionette || echo "Tor Browser failed to start"' > /usr/local/bin/start-tor-browser && \
    chmod +x /usr/local/bin/start-tor-browser && \
    chown -R 5001:5001 /opt/tor-browser

COPY user.js /opt/tor-browser/Browser/TorBrowser/Data/Browser/profile.default/user.js


RUN echo 'firefox --marionette' > /usr/local/bin/start-firefox && \
    chmod +x /usr/local/bin/start-firefox

# RUN wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux-aarch64.tar.gz && \
#     tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin && \
#     rm /tmp/geckodriver.tar.gz

COPY requirements.txt /tmp/requirements.txt
RUN python3.11 -m venv /venv
RUN /venv/bin/pip install -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt
