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
python3 run.py --build
python3 run.py --exec
```
