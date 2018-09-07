
import argparse
import os
import re
import requests
import subprocess

from . import config as es_config


def _match_to_node(match):
    return {"node": match.group("node"),
            "node-type": match.group("nodetype"),
            "zone": match.group("zone")}


def _get_nodes_by_type(nodetype):
    env = es_config.env()
    command = ['knife',
               'search',
               'role:elasticsearch6_{} AND chef_environment:{}'.format(nodetype, env),
               '-a',
               'ec2.placement_availability_zone']
    with open(os.devnull, 'w') as devnull:
        output = subprocess.check_output(command, stderr=devnull)

    pattern = re.compile(r'(?P<node>{}-es-(?P<nodetype>data-warm|data-hot|percolate)-\S+):\s+' \
                         r'ec2.placement_availability_zone:\s+us-west-2(?P<zone>[abc])'.format(env))
    return [ _match_to_node(match) for match in re.finditer(pattern, output.decode('utf8')) ]


def get_nodes(include_hot = True, include_warm = True, include_percolate = True):
    hot_nodes = _get_nodes_by_type('data_hot') if include_hot else []
    warm_nodes = _get_nodes_by_type('data_warm') if include_warm else []
    percolate_nodes = _get_nodes_by_type('percolate') if include_percolate else []

    return {node['node']: node for node in hot_nodes + warm_nodes + percolate_nodes}

