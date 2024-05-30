sudo chown vcantin:vcantin . -R
rm -rf services/redis/data/
git checkout .
git pull
docker compose down
docker compose up -d
echo "Script stated successfully!"
