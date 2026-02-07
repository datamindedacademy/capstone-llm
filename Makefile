.PHONY: requirements

requirements:
	uv export --format requirements-txt --no-dev > requirements.txt
