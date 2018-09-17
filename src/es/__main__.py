
import argparse
import errno
import logging

from .utils import config
config.reload_logging_level()

logger = logging.getLogger('__main__')


def _parse_args():
    parser = argparse.ArgumentParser(prog="es",
                                     description="Executes common commands against ES so you need to "
                                                 "craft fewer curls.")
    sp = parser.add_subparsers(dest="subcommand")
    sp.required = True

    sp_allocation = sp.add_parser('allocation',
                                  help="gets/sets the allocation policy of the cluster")
    sp_durability = sp.add_parser('durability',
                                  help="gets/sets the durability of all of today's indices")
    sp_move_shards = sp.add_parser('move-shards',
                                   help="helping hand for manually moving shards",
                                   description="Provides insights about shard distribution to help in deciding "
                                               "how to move shards between nodes.")
    sp_read_only = sp.add_parser('read-only',
                                 help="lists read-only indices in hot nodes",
                                 description="Searches the hot nodes for indices that are set to read-only "
                                             "(which can happen if disks are so full that they reach the high "
                                             "watermark of ES, which then decides it will stop accepting new data).")
    sp_shards = sp.add_parser('shards',
                              help="lists shards in hot, warm, and percolate nodes")

    sp_allocation.set_defaults(func=es_allocation)
    sp_durability.set_defaults(func=es_durability)
    sp_move_shards.set_defaults(func=es_move_shards)
    sp_read_only.set_defaults(func=es_read_only)
    sp_shards.set_defaults(func=es_shards)

    # Allocation
    group = sp_allocation.add_mutually_exclusive_group(required=False)
    group.add_argument('--show',
                       action='store_true',
                       help="shows the current setting for the cluster's allocation (default)")
    group.add_argument('--enable', '--all',
                       action='store_true',
                       help="enables allocation for the cluster")
    group.add_argument('--disable', '--none',
                       action='store_true',
                       help="disables allocation for the cluster")

    # Durability
    group = sp_durability.add_mutually_exclusive_group(required=False)
    group.add_argument('--show',
                       action='store_true',
                       help="shows the current setting for durability of today's indices (default)")
    group.add_argument('--async',
                       action='store_true',
                       help="changes the durability of today's indices to async")
    group.add_argument('--request',
                       action='store_true',
                       help="changes the durability of today's indices to request")
    sp_durability.add_argument('--date',
                               help="operate on another day's indices")

    # Move Shards
    group = sp_move_shards.add_mutually_exclusive_group(required=True)
    group.add_argument('--from',
                       dest='from_node',
                       help="node that has too many shards")
    group.add_argument('--to',
                       dest='to_node',
                       help="node that has too few shards")
    sp_move_shards.add_argument('-n',
                                dest='num_nodes',
                                type=int,
                                default=3,
                                help="how many nodes to suggest")
    sp_move_shards.add_argument('-s',
                                dest='num_shards',
                                type=int,
                                default=6,
                                help="how many shards to list per node")

    # Read-Only Shards
    sp_read_only.add_argument('--reset',
                              action='store_true',
                              help="remove any blocks from the indices on hot nodes")

    # Shards
    sp_shards.add_argument('-s', '--summary',
                           dest='summary',
                           action='store_true',
                           help="Show summarized distribution of shards per node")
    group = sp_shards.add_mutually_exclusive_group(required=False)
    group.add_argument('-w', '--warm',
                       dest='only_warm',
                       action='store_true',
                       help="Target warm nodes instead of hot nodes")
    group.add_argument('-p', '--percolate',
                       dest='only_percolate',
                       action='store_true',
                       help="Target percolator nodes instead of hot nodes")
    sp_shards.add_argument('-f', '--filter',
                           dest='filter',
                           action='store',
                           help="Only consider shards matching this regex")

    return parser.parse_args()


def es_allocation(args):
    from .commands import allocation
    allocation.execute(args)


def es_durability(args):
    from .commands import durability
    durability.execute(args)


def es_move_shards(args):
    from .commands import moveshards
    moveshards.execute(args)


def es_read_only(args):
    from .commands import readonly
    readonly.execute(args)


def es_shards(args):
    from .commands import shards
    shards.execute(args)


if __name__ == '__main__':
    args = _parse_args()

    try:
        args.func(args)
    except IOError as e:
        # A SIGPIPE is normal when `es-cli` is piped to a command that ends prematurely (like `es shards | head`)
        if e.errno == errno.EPIPE:
            logger.debug("Broken Pipe")
        else:
            raise
