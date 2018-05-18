[![Build Status](https://travis-ci.org/HumanCellAtlas/ingest-client.svg?branch=master)](https://travis-ci.org/HumanCellAtlas/ingest-broker)
[![Maintainability](https://api.codeclimate.com/v1/badges/c3cb9256f7e92537fa99/maintainability)](https://codeclimate.com/github/HumanCellAtlas/ingest-broker/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/c3cb9256f7e92537fa99/test_coverage)](https://codeclimate.com/github/HumanCellAtlas/ingest-broker/test_coverage)
[![Docker Repository on Quay](https://quay.io/repository/humancellatlas/ingest-demo/status "Docker Repository on Quay")](https://quay.io/repository/humancellatlas/ingest-demo)

# HCA Ingest Broker

Scripts for submitting spreadsheets of experimental metadata to the HCA. 
 
To run scripts locally you'll need python 3.6 and all the dependencies in [requirements.txt](requirements.txt).

```
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

# Web application 

## Running with Python 

Start the web application with 

```
python broker/broker_app.py
```

Alternatively, you can build and run the app with docker. To run the web application with docker for build the docker image with 

```
docker build . -t ingest-broker:latest
```

then run the docker container. You will need to provide the URL to the [Ingestion API](https://github.com/HumanCellAtlas/ingest-core)

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
 
This script will submit a HCA spreadsheet to the ingest API. 

```
python broker/hcaxlsbroker.py -p <path to excel file>
```

If you want to do a dry run to check the spreadsheet parses without submitting use the -d argument 

```
python broker/hcaxlsbroker.py -d -p <path to excel file>
```

## Bundle to spreadsheet 

This script will convert a set of data bundles in HCA JSON into an Excel file. It expects your bundles are in folders under your path like this
 \<supplied path\>/bundles/bundle*

```
python broker/bundle2xls.py -p <path to directory containing bundles>
```

## Export service

This script listens for submissions on the ingest API messaging queue. When a submission is valid and complete (i.e. all data files have been uploaded to the staging area) this script will run to generate the 
bundles and submit them to the HCA datastore. The export service needs the URL of the messaging queue along with the queue name. You can also override the URLs to the staging API and the DSS API.  To see all the argument use the --help argument. 

```
python export-to-dss.py
```

