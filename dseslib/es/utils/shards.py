
from functools import reduce
from operator import add
import re
import requests

from . import config as es_config
from . import humansize


def _match_to_shard(re_match):
    return {'node-type': re_match.group('nodetype'),
        'index': re_match.group('index'), 
        'num-shard': re_match.group('numshard'),
        'status': re_match.group('status'),
        'size': re_match.group('size'),
        'node': re_match.group('node')}


def get_shards(include_hot = True, include_warm = False, include_percolate = False, include_all_status = False):
    env = es_config.env()
    shard_regex = r'^(?P<index>\S+)\s+' \
                  r'(?P<numshard>\d+)\s+' \
                  r'[pr]\s+' \
                  r'(?P<status>\S+)\s+' \
                  r'\d+\s+' \
                  r'(?P<size>\S+)\s+' \
                  r'\S+\s+' \
                  r'(?P<node>{}-es-(?P<nodetype>data-hot|data-warm|percolate)-\S+)\s*' \
                  r'(?P<extra>.*)$'
    pattern = re.compile(shard_regex.format(env))
    r = requests.get("{}/_cat/shards".format(es_config.es_host()), stream=True)

    shards = []
    for shard_line in r.iter_lines():
        shard_line = shard_line.decode('utf8')
        match = pattern.match(shard_line)
        if match:
            shard = _match_to_shard(match)
            if include_hot and shard['node-type'] == 'data-hot':
                shards.append(shard)
                next
            if include_warm and shard['node-type'] == 'data-warm':
                shards.append(shard)
                next
            if include_percolate and shard['node-type'] == 'percolate':
                shards.append(shard)
                next

    # Remove non-started shards, unless we explicitly want them
    shards = [ shard for shard in shards if shard['status'] == 'STARTED' or include_all_status ]
    return shards


def summarize_shards(node, shards):
    shards_in_node = [ shard for shard in shards if shard['node'] == node ]
    if len(shards_in_node) == 0:
        return (0, 0)

    sizes = [ humansize.parse(shard['size']) for shard in shards_in_node ]
    size = reduce(add, sizes)

    return (len(shards_in_node), size)
