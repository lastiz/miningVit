test:
	-docker compose -f .\test-docker-compose.yml up --build --exit-code-from app
	docker compose -f .\test-docker-compose.yml down

run:
	docker compose up --build

rund:
	docker compose up -d

down:
	docker compose down