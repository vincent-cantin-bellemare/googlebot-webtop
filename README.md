# Googlebot - Webtop

## Installation

```sh
cd services/client
cp app/config.py.sample app/config.py
mkdir tor/ && cd tor/
wget -q -O ./tor-browser-linux64.tar.xz "https://www.torproject.org/dist/torbrowser/13.0.15/tor-browser-linux-x86_64-13.0.15.tar.xz"
sudo docker build -t googlebot-client:1.0.3 .
```

```sh
cd ../..
docker compose up -d
sudo chown $USER:$USER . -R
sudo chmod 777 services/client/volumes -R
```

# Crontab

```sh
0 * * * * cd /home/vcantin/docker/googlebot-webtop && docker compose down && docker compose up -d
```
