def generate_client_service(index):
    client_service = f"""
  client{index}:
    image: googlebot-client:1.0.3
    security_opt:
      - seccomp:unconfined
    entrypoint: [/init]
    volumes:
      - ./services/client/app:/app:r
      - ./logs:/logs
      - ./services/client/volumes/client_{index}/.cache:/config/.cache
    environment:
      - CLIENT_PORT={3000 + index * 10}
      - PUID=5001
      - PGID=5001
      - TZ=Etc/UTC
      - SUBFOLDER=/
      - TITLE=Webtop
    ports:
      - {3000 + index * 10}:3000
      - {3001 + index * 10}:3001
    shm_size: "1gb"
    restart: unless-stopped
"""
    return client_service

def main(num_clients):
    initial_compose_data = f"""
version: '3.8'

services:
  redis:
    image: redis/redis-stack-server:latest
    restart: unless-stopped
    ports:
      - 3380:6379/tcp
    volumes:
      - ./services/redis/data:/data:rw
    environment:
      REDIS_ARGS: "--appendonly yes"

  agent_1:
    image: python:latest
    build:
      context: services/agent
      dockerfile: Dockerfile
    environment:
      - AGENT_ID=1
    volumes:
      - ./services/agent/app:/app:r
      - ./logs:/logs
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
    command: sh -c "sleep 5 && python3 /app/run.py --execresults --fromindex 1 --toindex {num_clients - 2} && sleep infinity"

  agent_2:
    image: python:latest
    environment:
      - AGENT_ID=2
    build:
      context: services/agent
      dockerfile: Dockerfile
    volumes:
      - ./services/agent/app:/app:r
      - ./logs:/logs
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
    command: sh -c "sleep 5 && python3 /app/run.py --execurls --fromindex {num_clients - 2} --toindex {num_clients - 1} && sleep infinity"
    depends_on:
      - redis

  agent_3:
    image: python:latest
    environment:
      - AGENT_ID=3
    build:
      context: services/agent
      dockerfile: Dockerfile
    volumes:
      - ./services/agent/app:/app:r
      - ./logs:/logs
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
    command: sh -c "sleep 5 && python3 /app/run.py --execdomainsqueries --fromindex {num_clients - 1} --toindex {num_clients - 0} && sleep infinity"
    depends_on:
      - redis
"""

    # Generate client services
    new_services = ''

    for i in range(1, num_clients + 1):
        new_services += generate_client_service(i)

    # Combine initial compose data with new services
    updated_compose_data = initial_compose_data + new_services

    # Write the updated compose data to a new file
    with open(f'compose-{num_clients}.yml', 'w') as file:
        file.write(updated_compose_data)


if __name__ == '__main__':
    num_clients = int(input("Enter the number of client services to generate: "))
    main(num_clients)
