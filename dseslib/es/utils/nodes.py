
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
               'role:elasticsearch6_data_{} AND chef_environment:{}'.format(nodetype, env),
               '-a',
               'ec2.placement_availability_zone']
    with open(os.devnull, 'w') as devnull:
        output = subprocess.check_output(command, stderr=devnull)

    pattern = re.compile(r'(?P<node>{}-es-data-(?P<nodetype>warm|hot)-\S+):\s+' \
                         r'ec2.placement_availability_zone:\s+us-west-2(?P<zone>[abc])'.format(env))
    return [ _match_to_node(match) for match in re.finditer(pattern, output.decode('utf8')) ]


def get_nodes(include_hot = True, include_warm = True):
    hot_nodes = _get_nodes_by_type('hot') if include_hot else []
    warm_nodes = _get_nodes_by_type('warm') if include_warm else []

    return {node['node']: node for node in hot_nodes + warm_nodes }

