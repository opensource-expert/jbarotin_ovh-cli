# -*- encoding: utf-8 -*-
# aim of this script is to query different parameter of our OVH account

import configparser
import os


def get_config(key):
    config = configparser.ConfigParser()
    config.read(os.path.expanduser("~/.ovh-cli/secret"))
    if len(config.sections()) == 0:
        raise Exception("you must fill ovh secret in ~/.ovh-cli/secret")
    if key not in config.sections():
        raise Exception("section {} not found ".format(key))
    return config


def get_general(key="general"):
    config = get_config(key)
    return {
        "project_name": config[key].get('project_name'),
        "base_distrib": config[key].get('base_distrib'),
        "region": config[key].get('region'),
        "ssh_key_id": config[key].get('ssh_key_id'),
        "inventary_file": config[key].get('inventary_file'),
        "private_network_id": config[key].get('private_network_id'),
        "public_network_id": config[key].get('public_network_id')
    }


def get_ovh_connection_setting(key="get-info"):
    config = get_config(key)
    return {
        "application_key": config[key].get('application_key'),
        "application_secret": config[key].get('application_secret'),
        "consumer_key": config[key].get('consumer_key')
    }
