# Googlebot - Webtop

## Installation

```sh
cp app/config.py.sample app/config.py
mkdir tor/ && cd tor/
wget -q -O ./tor-browser-linux64.tar.xz "https://www.torproject.org/dist/torbrowser/13.0.15/tor-browser-linux-x86_64-13.0.15.tar.xz"
cd ..
docker build -t googlebot-client:1.0.0 .
docker compose up -d
```

### Scripts run

```sh
python3 run.py --execresults --fromindex 1 --toindex 11
python3 run.py --execurls --fromindex 1 --toindex 11
```
