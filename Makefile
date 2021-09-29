.PHONY : serve update test lint check-style tests fast-tests data-tests docker

serve : docker
	docker run --rm -it -p 8000:8000 -v ${PWD}:/awsipranges awsipranges:local

install : pyproject.toml
	poetry install

update : poetry-update requirements-dev.txt

poetry-update : pyproject.toml
	poetry update

poetry.lock : pyproject.toml
	poetry lock

requirements-dev.txt : poetry.lock
	poetry export --dev --without-hashes -o requirements-dev.txt

test : lint check-style tests

lint :
	flake8

check-style :
	black --check .

tests :
	pytest --cov=awsipranges

fast-tests :
	pytest --cov=awsipranges -m "not data and not extra_data_loading and not slow and not test_utils"

library-tests :
	pytest --cov=awsipranges --cov-report=xml -m "not data"

data-tests :
	pytest -m "data"

docker : Dockerfile requirements-dev.txt
	docker build -t awsipranges:local ./

publish-docs :
	mkdocs gh-deploy --force
