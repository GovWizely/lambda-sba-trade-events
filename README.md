[![CircleCI](https://circleci.com/gh/GovWizely/lambda-sba-trade-events/tree/master.svg?style=svg)](https://circleci.com/gh/GovWizely/lambda-sba-trade-events/tree/master)
[![Maintainability](https://api.codeclimate.com/v1/badges/0d4ddc12190e5e2239e9/maintainability)](https://codeclimate.com/github/GovWizely/lambda-sba-trade-events/maintainability)

# SBA Trade Events Lambda

This project provides an AWS Lambda that creates a single JSON document from the JSON endpoint 
at https://www.sba.gov/api/content/search/events.json that powers the search results page 
at https://www.sba.gov/events/find/?dateRange=all&distance=200&pageNumber=1.
It uploads that JSON file to a S3 bucket.

## Prerequisites

- This project is tested against Python 3.7+ in [CircleCI](https://app.circleci.com/github/GovWizely/lambda-sba-trade-events/pipelines).

## Getting Started

	git clone git@github.com:GovWizely/lambda-sba-trade-events.git
	cd lambda-sba-trade-events
	mkvirtualenv -p /usr/local/bin/python3.8 -r requirements-test.txt sba-trade-events

If you are using PyCharm, make sure you enable code compatibility inspections for Python 3.7/3.8.

### Tests

```bash
python -m pytest
```

## Configuration

* Define AWS credentials in either `config.yaml` or in the [default] section of `~/.aws/credentials`. To use another profile, you can do something like `export AWS_DEFAULT_PROFILE=govwizely`.
* Edit `config.yaml` if you want to specify a different AWS region, role, and so on.
* Make sure you do not commit the AWS credentials to version control.

## Invocation

	lambda invoke -v
 
## Deploy
    
To deploy:

	lambda deploy --requirements requirements.txt
