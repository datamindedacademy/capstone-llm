.PHONY: requirements

requirements:
	uv export --format requirements-txt --no-dev --no-emit-project > requirements.txt
