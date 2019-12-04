# -*- coding: utf-8 -*-
"""Creates a single JSON document from the JSON endpoint at
https://www.sba.gov/api/content/search/events.json. It uploads that JSON file to a S3
bucket. """
import json

import boto3
import requests

PAGINATION_OFFSET = 10
INITIAL_OFFSET = 0
JSON_ENDPOINT = "https://www.sba.gov/api/content/search/events.json?start={0}"
S3_CLIENT = boto3.resource('s3')


def handler(event, context):
    """
    Called by AWS Lambda service
    :param event: unused
    :param context: unused
    :return: str result
    """
    # pylint: disable=unused-argument
    entries = get_entries()
    if entries:
        S3_CLIENT.Object('trade-events', 'sba.json').put(Body=json.dumps(entries),
                                                         ContentType='application/json')
        return "Uploaded sba.json file with %i trade events" % len(entries)
    return "No entries loaded from %s so there is no JSON file to upload" % JSON_ENDPOINT


def get_entries():
    """Gets all valid entries from the JSON endpoint

    :return: list of entries
    """
    items = get_items()
    print "Found a total of {} events...".format(len(items))
    return items


def get_items():
    """Fetches items from `INITIAL_OFFSET` in batches of `PAGINATION_OFFSET` until there are no
    more """
    offset = INITIAL_OFFSET
    items = []
    while True:
        batch = get_page_of_items(JSON_ENDPOINT.format(offset))
        if not batch:
            break
        items.extend(batch)
        offset += PAGINATION_OFFSET
    return items


def get_page_of_items(url):
    """Gets one page of items
    :param url: The event-list URL with the appropriate offset
    :return: list of items
    """
    response = requests.get(url)
    response_json = response.json()
    # leaving this in here to debug intermittent errors with CloudFront-backed endpoint
    print response_json
    items = response_json['items']
    print "Found {} items from url {}".format(len(items), url)
    return items
