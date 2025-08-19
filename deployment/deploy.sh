docker build -f deployment/Dockerfile -t research-assistant .
docker compose -f deployment/docker-compose.yaml up --build -d
docker compose -f deployment/docker-compose.yaml ps