[![Build Status](https://travis-ci.org/HumanCellAtlas/ingest-client.svg?branch=master)](https://travis-ci.org/HumanCellAtlas/ingest-broker)
[![Maintainability](https://api.codeclimate.com/v1/badges/c3cb9256f7e92537fa99/maintainability)](https://codeclimate.com/github/HumanCellAtlas/ingest-broker/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/c3cb9256f7e92537fa99/test_coverage)](https://codeclimate.com/github/HumanCellAtlas/ingest-broker/test_coverage)
[![Docker Repository on Quay](https://quay.io/repository/humancellatlas/ingest-broker/status "Docker Repository on Quay")](https://quay.io/repository/humancellatlas/ingest-broker)

# HCA Ingest Broker

Web endpoint for submitting spreadsheets for HCA Ingest and basic admin UI. 
 
To run scripts locally you'll need Python 3.6 and all the dependencies in [requirements.txt](requirements.txt).

```
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

# Web Application 

## Running with Python 

Start the web application with 

```
python broker/broker_app.py
```

Alternatively, you can build and run the app with Docker. To run the web application with Docker for build the Docker image with 

```
docker build . -t ingest-broker:latest
```

then run the Docker container. You will need to provide the URL to the [Ingestion API](https://github.com/HumanCellAtlas/ingest-core)

```
docker run -p 5000:5000 -e INGEST_API=http://localhost:8080 ingest-broker:latest
```

or run against the development Ingest API
```
docker run -p 5000:5000 -e INGEST_API=http://api.ingest.dev.data.humancellatlas.org ingest-broker:latest
```

The application will be available at http://localhost:5000

# CLI application 


## Spreadsheet converter 
 
This script will submit a HCA spreadsheet to the Ingest API. 

```
python broker/hcaxlsbroker.py -p <path to excel file>
```

If you want to do a dry run to check the spreadsheet parses without submitting use the -d argument 

```
python broker/hcaxlsbroker.py -d -p <path to excel file>
```