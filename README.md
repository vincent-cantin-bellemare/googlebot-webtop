# Webtop

## Installation de l'image docker

1. Construire l'image Docker

```sh
docker pull lscr.io/linuxserver/webtop:ubuntu-mate
docker save lscr.io/linuxserver/webtop:ubuntu-mate -o webtopubuntumate.tar
docker load -i webtopubuntumate.tar
docker tag lscr.io/linuxserver/webtop:ubuntu-mate webtopubuntumate
docker tag webtopubuntumate vincentcodevolution/webtopubuntumate:latest
docker push vincentcodevolution/webtopubuntumate:latest
```

```sh
docker compose -p googlebotwebtopbuilder -f compose-builder.yaml down
docker compose -p googlebotwebtopbuilder -f compose-builder.yaml pull
docker compose -p googlebotwebtopbuilder -f compose-builder.yaml up --build --detach
```

2. Rouler le script

```sh
docker exec -it -u abc googlebotwebtopbuilder-app-1 bash -c 'cd /app && python3 run.py'
```

3. Accéder au [http://localhost:3000](http://localhost:3000)

4. Dans l'onglet Tor Browser, vous devriez vous faire demander de connecter automatiquement. Cliquer sur **Connecter automatiquement**

5. Lorsque Google Apparait, cliquer **Tout accepter**.

6. Sauvegarder l'image

```sh
docker ps | grep googlebotwebtopbuilder-app-1
docker commit cdfa75683c1d googlebotwebtopclients-app:v2024041703
docker stop cdfa75683c1d
docker rm cdfa75683c1d
```

# Démarrer le projet

### Manuellement

```sh
docker compose -p googlebotwebtopclients -f compose-clients.yaml down
docker compose -p googlebotwebtopclients -f compose-clients.yaml up --detach
docker exec -it -u abc googlebotwebtopclients-app1-1 bash -c 'cd /app && python3 run.py'
docker exec -it -u abc googlebotwebtopclients-app2-1 bash -c 'cd /app && python3 run.py'
docker exec -it -u abc googlebotwebtopclients-app3-1 bash -c 'cd /app && python3 run.py'
```

### Avec le script run

```sh
python3 run.py --build
python3 run.py --exec
```
