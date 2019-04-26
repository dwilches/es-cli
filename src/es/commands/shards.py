
import logging

from ..utils import shards as esshards
from ..utils import humansize
from ..types.nodes import NodeType

logger = logging.getLogger("es-shards")


def execute(args):
    if args.only_warm:
        node_type = NodeType.WARM
    elif args.only_percolate:
        node_type = NodeType.PERCOLATE
    else:
        node_type = NodeType.HOT

    shards = esshards.get_shards(node_type, include_all_status=True, shard_filter=args.filter)

    if args.summary:
        show_summary(shards)
    else:
        show_details(shards)


def show_details(shards):
    str_format = "{0:50s}\t{1}\t{2}\t{3}\t{4:35s}\t{5}\t{6}"
    print(str_format.format('INDEX', 'NUM', 'TYPE', 'SIZE', 'NODE', 'STATUS', ''))
    for shard in shards:
        print(str_format.format(shard.index,
                                shard.num_shard,
                                shard.shard_type,
                                shard.size,
                                shard.node or "(no node)",
                                shard.status,
                                shard.extra))


def show_summary(shards):
    summarized = esshards.summarize_shards(shards)
    total_count = 0
    total_size = 0

    str_format = "{0:40s}    {1}    {2}"
    print(str_format.format('NODE', 'NUM', 'SIZE'))
    for summary in sorted(summarized, key=lambda s: s.node):
        print(str_format.format(summary.node,
                                summary.amount,
                                humansize.stringify(summary.size)))
        total_count += summary.amount
        total_size += summary.size

    total_line = str_format.format('TOTAL', total_count, humansize.stringify(total_size))
    print('-' * len(total_line))
    print(total_line)
