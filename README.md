# Webtop

## Creation of new image

```sh
docker compose -p googlebotclient -f compose-template.yaml down
docker compose -p googlebotclient -f compose-template.yaml up --build --detach
docker exec -it -u abc googlebotclient-app-1 bash -c 'start-tor-browser'
docker exec -it -u abc googlebotclient-app-1 bash -c 'cd /app && python3 run.py'
# [cliquer sur connecter automatiquement + accepter google]
docker ps | grep googlebotclient-app-1
docker commit 738a1bee1e9b googlebotclient-app:v1
```

```sh
docker compose -p googlebotclient -f compose-clients.yaml down
docker compose -p googlebotclient -f compose-clients.yaml up --detach
docker exec -it -u abc googlebotclient-client1-1 bash -c 'cd /app && python3 run.py'
docker exec -it -u abc googlebotclient-client2-1 bash -c 'cd /app && python3 run.py'
docker exec -it -u abc googlebotclient-client3-1 bash -c 'cd /app && python3 run.py'
```
