sudo chown vcantin:vcantin . -R
git checkout .
git pull
docker compose down
docker compose up -d
echo "Script stated successfully!"
