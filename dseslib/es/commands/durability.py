
from datetime import datetime
import json
import re
import requests
import sys

from ..utils import config as es_config


def change_status(url, new_status):
    r = requests.put(url,
                     data = json.dumps({'index': {'translog': {'durability': new_status}}}),
                     headers = {'Content-Type': 'application/json'})
    r.raise_for_status()
    response = r.json()
    print("acknowledged: {}".format(response['acknowledged']))


def show_current_status(url):
    r = requests.get(url)
    settings = r.json()
    for index in sorted(settings.keys()):
        try:
            print("{}: {}".format(index, settings[index]["settings"]['index']['translog']['durability']))
        except KeyError:
            print("{}: default".format(index))


def execute(args):
    if args.date:
        if not re.match(r"\d{4}-\d\d-\d\d", args.date):
            print("Invalid date: {}".format(args.date))
            sys.exit(1)
        date = args.date
    else:
        date = datetime.today().strftime('%Y-%m-%d')

    url = "{}/{}-*-{}/_settings".format(es_config.es_host(),
                                        es_config.index_prefix(), date)

    if args.async:
        change_status(url, 'async')
        show_current_status(url)
    elif args.request:
        change_status(url, 'request')
        show_current_status(url)
    else:
        show_current_status(url)
