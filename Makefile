DOCKER_COMPOSE_FILE=docker-compose.yml
APP_FOLDER=app/
APP_NAME=fastapi-template

run:
	docker-compose -f $(DOCKER_COMPOSE_FILE) up --build -d

stop:
	docker-compose -f $(DOCKER_COMPOSE_FILE) stop

logs-app:
	docker logs -f $(APP_NAME)

format:
	uv run ruff format
	uv run ruff check --fix
	uv run pytest .