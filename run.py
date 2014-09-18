#!/usr/bin/env python
from ipop_stats.app import create as create_app
from flask import Flask
import argparse
import os, os.path

parser = argparse.ArgumentParser(description="Standalone test server for "
                                             "ipop-stats")

try:
    default_config_path = os.path.abspath(os.environ["IPOP_STATS_SETTINGS"])
except:
    default_config_path = "config/debug.yml"

parser.add_argument(
    "-c", "--config",
    default=default_config_path,
    type=os.path.abspath,
    help="the flask config file for the server"
)

args = parser.parse_args()
create_app(**vars(args)).run(host="0.0.0.0")
