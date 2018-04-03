"""Gitlab API command line client"""

import argparse
import os
import sys
import configparser

from pathlib import Path
from colorama import init

from . import APIClient
from .constants import *
from .config  import config
from .gitlab import Registry


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action")
    subparsers.required = True

    pipeline = subparsers.add_parser("pipeline")
    pipeline.add_argument("--list-jobs", action="store_true", dest="subitems")

    job = subparsers.add_parser("job")
    project = subparsers.add_parser("project")
    trace = subparsers.add_parser("trace")

    for sub in [pipeline, job, project, trace]:
        sub.add_argument("--project", type=int,
                         default=config["client"]["default_project"])
        group = sub.add_mutually_exclusive_group()
        group.add_argument("--item-id", "--id", type=int)
        group.add_argument("--list", action="store_true", dest="as_list")

    return parser.parse_args()


def show(item, inline=False):
    print(item.display(inline=inline))


def run(action, as_list=False, subitems=False, **kwargs):
    request = Registry.get_class_for(action)
    if not request:
        raise argparse.ArgumentTypeError("Undefined action {}", action)
    client = APIClient(config["client"])
    data = client.get(request.get_path(as_list=as_list, subitems=subitems, **kwargs))
    if as_list or subitems:
        [show(request(**item_data)) for item_data in data]
    else:
        show(request(**data))


def main():
    if config["ui"]["colors_enabled"]:
        init(autoreset=True)  # init colorama
    args = vars(parse_args())
    action = args.pop("action")
    run(action, **args)


if __name__ == "__main__":
    main()
