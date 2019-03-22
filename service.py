# -*- coding: utf-8 -*-
"""Creates a single JSON document from the JSON endpoint at
https://www.sba.gov/event-list/views/new_events_listing. It uploads that JSON file to a S3
bucket. """
import datetime as dt
import json

import boto3
import requests

INITIAL_OFFSET = 1500
LIMIT = 100
JSON_ENDPOINT = "https://www.sba.gov/event-list/views/new_events_listing?display_id=services_1" \
                "&filters[event_topic][value]=6&limit={0}&offset={1}"
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
    items = get_items()
    full_entries = [get_event(item) for item in items]
    print "Found a total of {} events...".format(len(full_entries))
    entries = [item for item in full_entries if is_valid(item)]
    print "...of which {} were valid events".format(len(entries))
    return entries


def get_items():
    """Fetches `LIMIT` items at a time starting from `INITIAL_OFFSET` until there are no more"""
    offset = INITIAL_OFFSET
    items = []
    while True:
        batch = get_page_of_items(JSON_ENDPOINT.format(LIMIT, offset))
        if not batch:
            break
        items.extend(batch)
        offset += LIMIT
    return items


def is_valid(event):
    """Determines if event is valid or not.
    :param event: The individual event from the JSON feed
    :return: bool
    """
    today = dt.date.today().strftime("%Y-%m-%d")
    country_exists = event['country']
    not_canceled = event['event_cancelled'] != 'Has been canceled'
    return event['event_date2_start'] > today and not_canceled and country_exists


def get_page_of_items(url):
    """Gets one page of `LIMIT` items
    :param url: The event-list URL with the appropriate offset
    :return: list of items
    """
    response = requests.get(url)
    items = response.json()
    print "Found {} items from url {}".format(len(items), url)
    return items


def get_event(event):
    """Extracts a normalized event from a JSON item
    :param event: The JSON item
    :return: An event dict
    """
    for key in event.keys():
        if ' ' in key:
            event[key.replace(' ', '_')] = event.pop(key)
    event['start_date'], event['start_time'], _, event['end_date'], event['end_time'] = event[
        'event_date'].split()
    if event['fee']:
        try:
            event['fee'] = float(event['fee'])
        except ValueError:
            event['fee'] = 0.0
    else:
        event['fee'] = 0.0
    return event
