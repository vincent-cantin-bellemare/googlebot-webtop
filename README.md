# Googlebot - Webtop

## Installation

### Manuellement

```sh
docker compose -p googlebotwebtop -f compose-clients.yaml down
docker compose -p googlebotwebtop -f compose-clients.yaml up --detach
docker exec -it -u abc googlebotwebtop-client1-1 bash -c 'cd /app && python3 run.py'
docker exec -it -u abc googlebotwebtop-client2-1 bash -c 'cd /app && python3 run.py'
docker exec -it -u abc googlebotwebtop-client3-1 bash -c 'cd /app && python3 run.py'
```

### Avec le script run

```sh
python3 run.py --compose
python3 run.py --build --fromindex 1 --toindex 5
python3 run.py --exec --fromindex 1 --toindex 5
```

Ubuntu Installation

```sh
sudo apt install nfs-common
sudo addgroup --system docker
sudo adduser $USER docker
newgrp docker
sudo usermod -aG docker $USER
sudo docker ps
sudo snap disable docker
sudo snap enable docker
sudo docker ps
```
