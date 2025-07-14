run:
	python -m app.app
test:
	mongosh --quiet --eval "db.getSiblingDB('iot').dropDatabase()"
	pytest
coverage:
	mongosh --quiet --eval "db.getSiblingDB('iot').dropDatabase()"
	pytest --cov=app --cov-report=html:html
	open html/index.html
docker:
	docker compose -f docker-compose.dev.yml -p telemetry up -d --build
docker-clear:
	docker container stop db-telemetry
	docker container stop app-telemetry

	docker container rm db-telemetry
	docker container rm app-telemetry

	docker image rm pomulo/app-telemetry:1.0
	docker image rm mongo:7.0.2

	docker compose -f docker-compose.dev.yml -p telemetry up -d --build
doc:
	PYTHONPATH=. pdoc app app.routes app.services --output-directory docs
	open docs/index.html