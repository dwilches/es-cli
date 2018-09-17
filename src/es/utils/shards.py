
from functools import reduce
from operator import add
import re
from typing import List

import requests

from . import config as es_config
from . import humansize
from ..types.shards import EsShard, SummarizedShards
from ..types.nodes import NodeType


def _match_to_shard(re_match) -> EsShard:
    return EsShard(index=re_match.group('index'),
                   num_shard=re_match.group('numshard'),
                   status=re_match.group('status'),
                   size=re_match.group('size'),
                   node=re_match.group('node'),
                   shard_type=re_match.group('shardtype'),
                   extra=re_match.group('extra'))


def get_shards(node_type: NodeType, include_all_status=False, shard_filter=None) -> List[EsShard]:
    """
        Retrieves the list of shards from ES and returns a list of EsShard. It respects the shard type and status type
        passed as parameters.
    """
    env = es_config.env()
    shard_regex = r'^(?P<index>\S+)\s+' \
                  r'(?P<numshard>\d+)\s+' \
                  r'(?P<shardtype>[pr])\s+' \
                  r'(?P<status>\S+)\s+' \
                  r'\d+\s+' \
                  r'(?P<size>\S+)\s+' \
                  r'\S+\s+' \
                  r'(?P<node>\S+)\s*' \
                  r'(?P<extra>.*)$'
    pattern = re.compile(shard_regex.format(env))
    lines = requests.get("{}/_cat/shards".format(es_config.es_host()), stream=True).iter_lines()

    shards = []
    for shard_line in lines:
        shard_line = shard_line.decode('utf8')
        match = pattern.match(shard_line)
        if match:
            shard = _match_to_shard(match)
            if _shard_matches_filter(shard, node_type, shard_filter, include_all_status):
                shards.append(shard)

    return shards


def summarize_shards(shards: List[EsShard]) -> List[SummarizedShards]:
    """
    Summarizes shards grouping them by node.
    """
    grouped = {}
    for shard in shards:
        if shard.node not in grouped:
            grouped[shard.node] = []

        grouped[shard.node].append(humansize.parse(shard.size))

    summaries = []
    for node, sizes in grouped.items():
        total_size = reduce(add, sizes)
        summaries.append(SummarizedShards(node=node,
                                          size=total_size,
                                          amount=len(sizes)))
    return summaries


def _shard_matches_filter(shard, included_node_types, shard_filter, include_all_status):

    node_type_matches = (included_node_types & NodeType.HOT and '-hot-' in shard.node) or \
                        (included_node_types & NodeType.WARM and '-warm-' in shard.node) or \
                        (included_node_types & NodeType.PERCOLATE and '-percolate-' in shard.node)

    node_status_matches = shard.status == 'STARTED' or include_all_status

    filter_matches = re.search(shard_filter, shard.index) if shard_filter else True

    return node_type_matches and node_status_matches and filter_matches
