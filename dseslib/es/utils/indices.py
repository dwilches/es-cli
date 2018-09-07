
import argparse
import json
import os
import re
import requests
import subprocess

from . import config as es_config
from . import shards as esshards

_re_date = re.compile(r"\S+-(\d{4}-\d\d-\d\d)")


# Returns the dates for which we have data in the hot nodes
def get_dates_hot_nodes():
    hot_indices = get_indices()
    matches = [ _re_date.match(index_name) for index_name in hot_indices ]
    return set([ match.group(1) for match in matches if match ])


def get_indices(include_hot = True, include_warm = False, include_percolate = False):
    shards = esshards.get_shards(include_hot, include_warm, include_percolate)
    return set([ shard['index'] for shard in shards ])


def get_readonly_hot_indices():
    hot_dates = get_dates_hot_nodes()

    # Request a list of read-only-indices for each of the hot_dates
    all_blocks = {}
    for date in hot_dates:
        r = requests.get("{}/{}-*-{}/_settings".format(es_config.es_host(), es_config.index_prefix(), date),
                         stream = True)
        r.raise_for_status()
        for index, settings in r.json().items():
            try:
                blocks = settings['settings']['index']['blocks']
                if blocks is not None:
                    all_blocks[index] = list(blocks.keys())
            except KeyError:
                pass
    return all_blocks


def reset_readonly_hot_indices():
    hot_dates = get_dates_hot_nodes()

    dates_reset = {}
    for date in hot_dates:
        r = requests.put("{}/{}-*-{}/_settings".format(es_config.es_host(), es_config.index_prefix(), date),
                         data = json.dumps({'index.blocks.read_only_allow_delete': None}),
                         headers = {'Content-Type': 'application/json'},
                         stream = True)
        r.raise_for_status()
        response = r.json()
        dates_reset[date] = response['acknowledged']
    
    return dates_reset
