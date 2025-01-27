#!/usr/bin/env python
import argparse
import sys

from rotkehlchen.config import default_data_directory
from rotkehlchen.utils.misc import get_system_spec


class VersionAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):  # pylint: disable=unused-argument
        super().__init__(option_strings, dest)

    def __call__(self, parser, namespace, values, option_string=None):
        print(get_system_spec()['rotkehlchen'])
        sys.exit(0)


def app_args(prog: str, description: str) -> argparse.ArgumentParser:
    """Add the Rotkehlchen arguments to the argument parser and return it"""
    p = argparse.ArgumentParser(
        prog=prog,
        description=description,
    )

    p.add_argument(
        '--output',
        help=(
            'A path to a file for logging all output. If nothing is given'
            'stdout is used'
        ),
    )
    p.add_argument(
        '--sleep-secs',
        type=int,
        default=20,
        help="Seconds to sleep during the main loop",
    )
    p.add_argument(
        '--notify',
        action='store_true',
        help=(
            'If given then the tool will send notifications via '
            'notify-send.'
        ),
    )
    p.add_argument(
        '--data-dir',
        help='The directory where all data and configs are placed',
        default=default_data_directory(),
    )
    p.add_argument(
        '--zerorpc-port',
        help='The port on which to open a zerorpc server for communication with the UI',
        default=4242,
    )
    p.add_argument(
        '--ethrpc-port',
        help="The port on which to communicate with an ethereum client's RPC.",
        default=8545,
    )
    p.add_argument(
        '--logfile',
        help='The name of the file to write log entries to',
        default='rotkehlchen.log',
    )
    p.add_argument(
        '--logtarget',
        help='Choose where logging entries will be sent. Valid values are "file and "stdout"',
        choices=['stdout', 'file'],
        default='file',
    )
    p.add_argument(
        '--loglevel',
        help='Choose the logging level',
        choices=['debug', 'info', 'warn', 'error', 'critical'],
        default='debug',
    )
    p.add_argument(
        '--logfromothermodules',
        help=(
            'If given then logs from all imported modules that use the '
            'logging system will also be visible.'
        ),
        action='store_true',
    )
    p.add_argument(
        'version',
        help='Shows the rotkehlchen version',
        action=VersionAction,
    )

    return p
