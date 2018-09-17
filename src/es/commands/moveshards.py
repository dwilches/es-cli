
import sys
from typing import Dict

from ..types.shards import SummarizedShards
from ..types.nodes import NodeType
from ..utils import shards as esshards
from ..utils import nodes as esnodes
from ..utils import humansize


# Prints the N1 smallest and N2 largest shards in the given node (or viceversa, it doesn't matter)
def _print_some_shards(node, shards, num_shards, indentation, reverse=False):
    shards_in_node = [shard for shard in shards if shard['node'] == node]
    sorted_shards = sorted(shards_in_node, key=lambda x: humansize.parse(x['size']),
                           reverse=reverse)

    N = min(num_shards, len(shards_in_node))
    N1 = N // 2
    N2 = N - N1

    for shard in sorted_shards[:N1]:
        print("{}* {} {} ({})".format(indentation, shard['index'], shard['num-shard'], shard['size']))
    if N1 + N2 < len(shards_in_node):
        print("{}  ...".format(indentation))
    for shard in sorted_shards[-N2:]:
        print("{}* {} {} ({})".format(indentation, shard['index'], shard['num-shard'], shard['size']))


def execute(args):
    # Get the details of the node passed in --from or --to
    partial_name = args.from_node if args.from_node else args.to_node
    hot_nodes = esnodes.get_nodes(True, False, False)
    matches = [node_name for node_name in hot_nodes.keys() if partial_name in node_name]

    if len(matches) == 0:
        print("No node matches the given value: {}".format(partial_name))
        sys.exit(1)

    if len(matches) > 1:
        print("Multiple nodes match the given value: {}".format(partial_name))
        [print("\t* {}".format(node)) for node in matches]
        sys.exit(1)

    desired_node = hot_nodes[matches[0]]

    # Find all other nodes in the same AZ
    nodes_same_az = [node for node in hot_nodes.values()
                     if node['zone'] == desired_node['zone'] and node is not desired_node]
    if len(nodes_same_az) == 0:
        print("There are {} nodes, but none in the same AZ as {}".format(len(hot_nodes), desired_node['node']))
        sys.exit(1)

    # Find shard distribution to recommend where to move the shards
    shards = esshards.get_shards(NodeType.HOT)
    summaries = esshards.summarize_shards(shards)
    shard_distribution: Dict[str, SummarizedShards] = {summary.node: summary for summary in summaries
                                                       if summary.node in nodes_same_az}
    (curr_num_shards, curr_size) = next(summary for summary in summaries if summary.node == desired_node.node)

    # Find the 3 nodes with fewer shards
    fewer_shards = sorted(shard_distribution, key=lambda x: shard_distribution[x].amount)
    smaller_size = sorted(shard_distribution, key=lambda x: shard_distribution[x].size)

    if args.from_node:
        print("The node {} from where you want to move shards has {} shards ({})."
              .format(desired_node['node'], curr_num_shards, humansize.stringify(curr_size)))
        _print_some_shards(desired_node['node'], shards, args.num_shards, '\t')
        print()
        print("From the nodes in the same AZ, these are the {} with fewer shards:".format(args.num_nodes))
        for node in fewer_shards[:args.num_nodes]:
            print("\t* {}: {} shards ({})".format(node,
                                                  shard_distribution[node].amount,
                                                  humansize.stringify(shard_distribution[node].size)))
        print()
        print("From the nodes in the same AZ, these are the {} with smaller shards:".format(args.num_nodes))
        for node in smaller_size[:args.num_nodes]:
            print("\t* {}: {} shards ({})".format(node,
                                                  shard_distribution[node].amount,
                                                  humansize.stringify(shard_distribution[node].size)))

    if args.to_node:
        print("The node to which you want to move shards has {} shards ({})."
              .format(curr_num_shards, humansize.stringify(curr_size)))
        print()
        print("From the nodes in the same AZ, these are the {} with more shards:".format(args.num_nodes))

        for node in list(reversed(fewer_shards))[:args.num_nodes]:
            print("\t* {}: {} shards ({})".format(node,
                                                  shard_distribution[node].amount,
                                                  humansize.stringify(shard_distribution[node].size)))
            _print_some_shards(node, shards, args.num_shards, '\t\t', reverse=True)
            print()
        print()
        print("From the nodes in the same AZ, these are the {} with larger shards:".format(args.num_nodes))
        for node in list(reversed(smaller_size))[:args.num_nodes]:
            print("\t* {}: {} shards ({})".format(node,
                                                  shard_distribution[node].amount,
                                                  humansize.stringify(shard_distribution[node].size)))
            _print_some_shards(node, shards, args.num_shards, '\t\t', reverse=True)
            print()
