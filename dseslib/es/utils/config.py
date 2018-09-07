
import json
import os

_config_file_name = "/etc/es-cli.cfg"
with open(_config_file_name) as config_fp:
    _config = json.load(config_fp)


def env():
    return _get_config("ES_CLI_ENV")


def es_host():
    return _get_config("ES_CLI_HOST")


def index_prefix():
    return _get_config("ES_CLI_INDEX_PREFIX")


def _get_config(name):
    """
        Returns the value for the config variable called "name" from the environment variables or the config file.
        It gives priority to variables in the environment.
    """
    value = os.getenv(name)
    if value:
        return value

    if name in _config:
        return _config[name]

    raise KeyError("Missing {} variable in the environment and config file ({}).".format(
        name, _config_file_name))
