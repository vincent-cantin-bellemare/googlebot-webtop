# Googlebot - Webtop

## Installation

```sh
mkdir tor/ && cd tor/
wget -q -O ./tor-browser-linux64.tar.xz "https://www.torproject.org/dist/torbrowser/13.0.14/tor-browser-linux-x86_64-13.0.14.tar.xz"
docker build -t googlebot-client:1.0.0 .
docker compose up -d
```

### Scripts run

```sh
python3 run.py --compose
python3 run.py --build --fromindex 1 --toindex 11
python3 run.py --execresults --fromindex 1 --toindex 11
python3 run.py --execurls --fromindex 1 --toindex 11
```
