# -*- coding: utf-8 -*-
"""Creates a single JSON document from the RSS endpoint at
https://www.sba.gov/event-list/views/new_events_listing based on data from
https://www.sba.gov/tools/events. It uploads that JSON file to a S3 bucket. """
import datetime as dt
import json
import xml.etree.ElementTree as ET

import bleach
import boto3
import requests

INITIAL_OFFSET = 1200
LIMIT = 100
XML_ENDPOINT = "https://www.sba.gov/event-list/views/new_events_listing?display_id=services_1" \
               "&filters[event_topic][value]=6&limit={0}&offset={1}"
TAGS = ['fee', 'body', 'event_cancelled', 'node_title', 'event_type', 'registration_website',
        'event_date', 'time_zone']
CONTACT_TAGS = ['contact_name', 'registration_phone', 'registration_email', 'agency']
VENUE_TAGS = ['city', 'country', 'street', 'location_name', 'province', 'postal_code']
TAGS_TO_SANITIZE = ['body', 'street']
US_STATES = {'Mississippi': 'MS', 'Northern Mariana Islands': 'MP', 'Oklahoma': 'OK',
             'Wyoming': 'WY', 'Minnesota': 'MN', 'Alaska': 'AK', 'American Samoa': 'AS',
             'Arkansas': 'AR', 'New Mexico': 'NM', 'Indiana': 'IN', 'Maryland': 'MD',
             'Louisiana': 'LA', 'Texas': 'TX', 'Tennessee': 'TN', 'Iowa': 'IA', 'Wisconsin': 'WI',
             'Arizona': 'AZ', 'Michigan': 'MI', 'Kansas': 'KS', 'Utah': 'UT', 'Virginia': 'VA',
             'Oregon': 'OR', 'Connecticut': 'CT', 'District of Columbia': 'DC',
             'New Hampshire': 'NH', 'Idaho': 'ID', 'West Virginia': 'WV', 'South Carolina': 'SC',
             'California': 'CA', 'Massachusetts': 'MA', 'Vermont': 'VT', 'Georgia': 'GA',
             'North Dakota': 'ND', 'Pennsylvania': 'PA', 'Puerto Rico': 'PR', 'Florida': 'FL',
             'Hawaii': 'HI', 'Kentucky': 'KY', 'Rhode Island': 'RI', 'Nebraska': 'NE',
             'Missouri': 'MO', 'Ohio': 'OH', 'Alabama': 'AL', 'Illinois': 'IL',
             'Virgin Islands': 'VI', 'South Dakota': 'SD', 'Colorado': 'CO', 'New Jersey': 'NJ',
             'National': 'NA', 'Washington': 'WA', 'North Carolina': 'NC', 'Maine': 'ME',
             'New York': 'NY', 'Montana': 'MT', 'Nevada': 'NV', 'Delaware': 'DE', 'Guam': 'GU',
             'District Of Columbia': 'DC'}
S3_CLIENT = boto3.resource('s3')
SESSION = requests.Session()
SESSION.headers.update({'Accept': 'application/xml'})


def handler(event, context):
    """
    Called by AWS Lambda service
    :param event: unused
    :param context: unused
    :return: str result
    """
    # pylint: disable=unused-argument
    items = get_items()
    full_entries = [get_event(item) for item in items]
    entries = [item for item in full_entries if is_valid(item)]
    if entries:
        S3_CLIENT.Object('trade-events', 'sba.json').put(Body=json.dumps(entries),
                                                         ContentType='application/json')
        return "Uploaded sba.json file with %i trade events" % len(entries)
    return "No entries loaded from %s so there is no JSON file to upload" % XML_ENDPOINT


def get_items():
    """Fetches `LIMIT` items at a time starting from `INITIAL_OFFSET` until there are no more"""
    print "Fetching XML feed of items..."
    offset = INITIAL_OFFSET
    items = []
    while True:
        batch = get_page_of_items(XML_ENDPOINT.format(LIMIT, offset))
        if not batch:
            break
        items.extend(batch)
        offset += LIMIT
    return items


def is_valid(event):
    """Determines if event is valid or not.
    :param event: The individual event from the XML feed
    :return: bool
    """
    today = dt.date.today().strftime("%Y-%m-%d")
    country_exists = event['venues'][0]['country']
    not_canceled = event['event_cancelled'] != 'Has been canceled'
    return event['start_date'] > today and not_canceled and country_exists


def get_page_of_items(url):
    """Gets one page of `LIMIT` items
    :param url: The event-list URL with the appropriate offset
    :return: list of items
    """
    response = SESSION.get(url)
    root = ET.fromstring(response.text.encode('utf-8'))
    items = root.findall('./item')
    print "Found {} items from url {}".format(len(items), url)
    return items


def get_event(item):
    """Extracts an event from an XML item
    :param item: The XML item
    :return: An event dict
    """
    event = {tag: get_text(item, tag) for tag in TAGS}
    event['start_date'], event['start_time'], _, event['end_date'], event['end_time'] = event[
        'event_date'].split()
    event['contacts'] = get_contacts(item)
    event['venues'] = get_venues(item)
    if event['fee']:
        try:
            event['fee'] = float(event['fee'])
        except ValueError:
            event['fee'] = 0.0
    else:
        event['fee'] = 0.0
    return event


def get_venues(item):
    """Extracts venues from an item
    :param item: The XML item
    :return: list of venues
    """
    venue = {tag: get_text(item, tag) for tag in VENUE_TAGS}
    unicode_state_name = unicode(venue['province'])
    if unicode_state_name:
        print "Looking up state :{}:".format(unicode_state_name)
        venue['province'] = US_STATES[unicode_state_name]
    return [venue]


def get_contacts(item):
    """Extracts contacts from an item

    :param item: The XML item
    :return: list of contacts
    """
    contact = {tag: get_text(item, tag) for tag in CONTACT_TAGS}
    return [contact]


def get_text(item, tag):
    """Extracts sanitized inner text from specified field

    :param item: The XML item
    :param tag: The tag to extract and sanitize
    :return: Result str
    """
    inner_text = get_inner_text(item, tag)
    result_text = '{}'.format(inner_text)
    if tag in TAGS_TO_SANITIZE:
        result_text = bleach.clean(result_text, strip=True)
    return result_text


def get_inner_text(item, tag):
    """Extracts inner text from specified field

    :param item: The XML item
    :param tag: The tag to extract inner text from
    :return: Result str
    """
    element = item.find(tag)
    try:
        element_text = element.text.encode('utf8')
    except AttributeError:
        element_text = ""
    return element_text
