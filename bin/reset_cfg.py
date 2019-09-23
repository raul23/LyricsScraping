#!/usr/bin/env python
"""Script to reset a config file.

The configuration file can either be:
- the main configuration file : used for configuring a lyrics scraper
- the logging configuration file : used to set up the logging for all custom
                                   modules

Once the config file is reset, it will be updated with all the default values.

TODO: add script usage

"""

import argparse
# Custom modules
from lyrics_scraping.utils import get_config_filepath
from pyutils.genutils import copy_file


def main():
    # Setup the parser
    parser = argparse.ArgumentParser(
        description="Reset a configuration file which can either be the "
                    "logging or the main config file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-f", "--cfg_file",
        required=True,
        choices=["log", "main"],
        help="What config file to reset: 'log' for the logging config file "
             "and 'main' for the main config file.")
    args = parser.parse_args()
    # TODO: add comments
    orig_cfg_filepath = get_config_filepath(cfg_type=args.cfg_file, orig=True)
    user_cfg_filepath = get_config_filepath(cfg_type=args.cfg_file, orig=False)
    try:
        copy_file(source_filepath=orig_cfg_filepath,
                  dest_filepath=user_cfg_filepath)
    except OSError as e:
        print(e)
    else:
        print("The {} configuration file is reset".format(args.cfg_file))


if __name__ == '__main__':
    main()
