# Makefile

COMPOSE_FILE=deploy/docker-compose.yml
ENV_FILE=.env

.PHONY: up down restart logs ps

up:
	@echo "🚀 Starting services..."
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d --build

down:
	@echo "🛑 Stopping services..."
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down

restart: down up

logs:
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f

ps:
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE) ps