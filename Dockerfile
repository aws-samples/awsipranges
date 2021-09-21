# Dockerfile for running the docs development server locally
FROM python:3.8

WORKDIR /awsipranges

ENV PYTHONPATH=/awsipranges

# Install Python dependencies
COPY requirements-dev.txt ./
RUN pip install -r requirements-dev.txt

EXPOSE 8000

CMD ["mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]
