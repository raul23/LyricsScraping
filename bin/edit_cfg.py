#!/usr/bin/env python
"""Script to edit a configuration file.

The configuration file can either be:
- the main configuration file : used for configuring a lyrics scraper
- the logging configuration file : used to set up the logging for all custom
                                   modules

Usage
-----
    $ edit_cfg.py [-h] [-a APP] -f {log,main}

Edit the main config file with TextEdit (macOS):
    $ edit_cfg.py -a TextEdit -f main

Edit the logging config file with default application (e.g. atom):
    $ edit_cfg.py -f log

Available options:
    -h, --help            show this help message and exit
    -a APP, --app_name APP
                        Name of the application to use for editing the file.
                        If no name is given, then the default application for
                        opening this type of file will be used. (default:
                        None)
    -f {log,main}, --cfg_file {log,main}
                        What config file to edit: 'log' for the logging config
                        file and 'main' for the main config file. (default:
                        None)

"""

import argparse
import platform
import sys
# Custom modules
from lyrics_scraping.utils import get_config_filepath
from pyutils.genutils import run_cmd


def main():
    # Setup the parser
    parser = argparse.ArgumentParser(
        description="Edit a configuration file which can either be the "
                    "logging or the main config file.",
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
    args = parser.parse_args()
    app = args.app
    filepath = get_config_filepath(args.cfg_file)
    # TODO: add comments
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
        if retcode:
            print("Return code is ", retcode)
        sys.exit(retcode)


if __name__ == '__main__':
    main()
