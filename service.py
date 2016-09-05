# -*- coding: utf-8 -*-
import json
import ssl
import xml.etree.ElementTree as ET

import boto3
import datetime as dt
import requests
import us
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager


class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


INITIAL_OFFSET = 800
LIMIT = 100
XML_ENDPOINT = "https://www.sba.gov/event-list/views/new_events_listing?display_id=services_1&filters[event_topic][value]=6&limit={0}&offset={1}"
TAGS = ['fee', 'body', 'event_cancelled', 'node_title', 'event_type', 'registration_website', 'event_date', 'time_zone']
CONTACT_TAGS = ['contact_name', 'registration_phone', 'registration_email', 'agency']
VENUE_TAGS = ['city', 'country', 'street', 'location_name', 'province', 'postal_code']

s3 = boto3.resource('s3')


def handler(event, context):
    items = get_items()
    full_entries = [get_event(item) for item in items]
    entries = [item for item in full_entries if is_valid(item)]
    if len(entries) > 0:
        s3.Object('trade-events', 'sba.json').put(Body=json.dumps(entries), ContentType='application/json')
        return "Uploaded sba.json file with %i trade events" % len(entries)
    else:
        return "No entries loaded from %s so there is no JSON file to upload" % XML_ENDPOINT


def get_items():
    print "Fetching XML feed of items..."
    s = requests.Session()
    s.mount('https://', MyAdapter())
    s.headers.update({'Accept': 'application/xml'})
    offset = INITIAL_OFFSET
    items = []
    while True:
        batch = get_page_of_items(s, XML_ENDPOINT.format(LIMIT, offset))
        if len(batch) == 0:
            break
        items.extend(batch)
        offset += LIMIT
    return items


def is_valid(event):
    today = dt.date.today().strftime("%Y-%m-%d")
    return event['start_date'] > today and event['event_cancelled'] != 'Has been canceled' and event['venues'][0][
        'country']


def get_page_of_items(s, url):
    response = s.get(url)
    root = ET.fromstring(response.text.encode('utf-8'))
    items = root.findall('./item')
    print "Found %i items" % len(items)
    return items


def get_event(item):
    event = {tag: get_text(item, tag) for tag in TAGS}
    event['start_date'], event['start_time'], sep, event['end_date'], event['end_time'] = event['event_date'].split()
    event['contacts'] = get_contacts(item)
    event['venues'] = get_venues(item)
    if len(event['fee']) > 0:
        event['fee'] = float(event['fee'])
    else:
        event['fee'] = 0.0
    return event


def get_venues(item):
    return [get_venue(item)]


def get_venue(item):
    venue = {tag: get_text(item, tag) for tag in VENUE_TAGS}
    unicode_state_name = unicode(venue['province'])
    if unicode_state_name:
        venue['province'] = us.states.lookup(unicode_state_name).abbr
    return venue


def get_contacts(item):
    return [get_contact(item)]


def get_contact(item):
    contact = {tag: get_text(item, tag) for tag in CONTACT_TAGS}
    return contact


def get_text(item, tag):
    inner_text = get_inner_text(item, tag)
    result_text = '{}'.format(inner_text)
    return result_text


def get_inner_text(item, tag):
    element = item.find(tag)
    try:
        element_text = element.text.encode('utf8')
    except AttributeError:
        element_text = ""
    return element_text
