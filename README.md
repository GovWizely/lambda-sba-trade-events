[![CircleCI](https://circleci.com/gh/GovWizely/lambda-sba-trade-events/tree/master.svg?style=svg)](https://circleci.com/gh/GovWizely/lambda-sba-trade-events/tree/master)
# SBA Trade Events Lambda

This project provides an AWS Lambda that creates a single JSON document from the JSON endpoint 
at https://www.sba.gov/event-list/views/new_events_listing.
It uploads that JSON file to a S3 bucket.

## Prerequisites

Follow instructions from [python-lambda](https://github.com/nficano/python-lambda) to ensure your basic development environment is ready,
including:

* Python
* Pip
* Virtualenv
* Virtualenvwrapper
* AWS credentials

## Getting Started

	git clone git@github.com:GovWizely/lambda-sba-trade-events.git
	cd lambda-sba-trade-events
	mkvirtualenv -r requirements.txt sba-trade-events

## Configuration

* Define AWS credentials in either `config.yaml` or in the [default] section of ~/.aws/credentials. To use another profile, you can do something like `export AWS_DEFAULT_PROFILE=govwizely`.

* Edit `config.yaml` if you want to specify a different AWS region, role, and so on.
* Make sure you do not commit the AWS credentials to version control

## Invocation

	lambda invoke -v
 
## Deploy

	lambda deploy
