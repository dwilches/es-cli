
import requests
import json

from ..utils import config as es_config


def change_status(url, new_status):
    r = requests.put(url,
                     data=json.dumps({'transient': {'cluster.routing.allocation.enable': new_status}}),
                     headers={'Content-Type': 'application/json'})
    r.raise_for_status()
    response = r.json()
    print("acknowledged: {}".format(response['acknowledged']))
    print("allocation: {}".format(response['transient']['cluster']['routing']['allocation']['enable']))


def show_current_status(url):
    r = requests.get(url)
    settings = r.json()
    print(settings['transient']['cluster']['routing']['allocation']['enable'])


def execute(args):
    url = "{}/_cluster/settings".format(es_config.es_host())

    if args.enable:
        change_status(url, "all")
    elif args.disable:
        change_status(url, "none")
    else:
        show_current_status(url)
