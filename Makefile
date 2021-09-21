.PHONY : serve update docker

serve : docker
	docker run --rm -it -p 8000:8000 -v ${PWD}:/awsipranges awsipranges:local

update : pyproject.toml
	poetry update

docker : Dockerfile requirements-dev.txt
	docker build -t awsipranges:local ./

poetry.lock : pyproject.toml
	poetry lock

requirements-dev.txt : poetry.lock
	poetry export --dev --without-hashes -o requirements-dev.txt
