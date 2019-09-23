#!/usr/bin/env python
"""Script to edit a configuration file.

The configuration file can either be:
- the main configuration file : used for configuring a lyrics scraper
- the logging configuration file : used to set up the logging for all custom
                                   modules

TODO: add usage

"""
import argparse
import os
import platform
import shlex
import subprocess
import ipdb
# Custom modules
from lyrics_scraping import data


def run_cmd(cmd):
    try:
        retcode = subprocess.check_call(shlex.split(cmd))
    except subprocess.CalledProcessError as e:
        return e.returncode
    else:
        return retcode


def main():
    # Setup the parser
    # TODO: add name of config file in description
    parser = argparse.ArgumentParser(
        description="Edit the main configuration file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-a",
                        "--app_name",
                        default=None,
                        dest="app",
                        help="Name of the application to use for editing the "
                             "file. If no name is given, then the default "
                             "application for opening this type of file will "
                             "be used.")
    parser.add_argument(
        "-f", "--cfg_file",
        required=True,
        choices=["log", "main"],
        help="What config file to edit: 'log' for the logging config file and "
             "'main' for the main config file.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Increase output verbosity")
    args = parser.parse_args()
    app = args.app
    if args.cfg_file == "log":
        filepath = os.path.join(data.__path__[0], 'logging_cfg.yaml')
    else:
        filepath = os.path.join(data.__path__[0], 'main_cfg.yaml')
    default_app_dict = {'Darwin': 'open {path}',
                        'Windows': 'cmd /c start "" "{path}"'}
    default_cmd = default_app_dict.get(platform.system(), 'xdg-open {path}')
    cmd = default_cmd if app is None else app + " " + filepath
    retcode = None
    try:
        retcode = run_cmd(cmd.format(path=filepath))
    except FileNotFoundError as e:
        # e.g. the app name is not found
        specific_app_dict = {'Darwin': 'open -a {app}'.format(app=app)}
        cmd = specific_app_dict.get(platform.system(), app)
        cmd += " " + filepath
        retcode = run_cmd(cmd)
    finally:
        print(retcode)


if __name__ == '__main__':
    main()
