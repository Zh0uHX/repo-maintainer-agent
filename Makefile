.PHONY: api demo install lint test

install:
	python3 -m pip install -e '.[api,dev]'

test:
	python3 -m unittest discover -s tests -v

lint:
	ruff check .
	ruff format --check .

demo:
	python3 -m repoagent demo

api:
	uvicorn repoagent.api:app --host 127.0.0.1 --port 8000
