
import logging
import os
import yaml


_config_file_name = "/etc/es-cli.cfg"
with open(_config_file_name) as config_fp:
    _config = yaml.load(config_fp)

env_vars = {
    "env": "ES_CLI_ENV",
    "host": "ES_CLI_HOST",
    "index_prefix": "ES_CLI_INDEX_PREFIX",
    "log_level": "ES_CLI_LOG_LEVEL",
}


def env():
    return _get_config("env")


def es_host():
    return _get_config("host")


def index_prefix():
    return _get_config("index_prefix")


def _get_config(name):
    """
        Returns the value for the config variable called "name" from the environment variables or the config file.
        It gives priority to variables in the environment.
    """
    value = os.getenv(env_vars[name])
    if value:
        return value

    # If var is not overriden in the env, check the file
    if name in _config:
        return _config[name]

    raise KeyError("Missing '{}' variable in the environment and config file ({}).".format(
        name, _config_file_name))


def reload_logging_level():
    logging.basicConfig(level=_get_config("log_level"))
