build:
	docker compose build

up:
	docker compose --profile dev up -d

down: 
	docker compose --profile dev down

rm:
	docker compose --profile dev down -v --remove-orphans

watch:
	docker compose --profile dev watch
