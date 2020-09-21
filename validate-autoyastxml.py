#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
from logging.config import dictConfig
from urllib.request import urlopen
import sys
from socket import getfqdn

__author__ = "Martin Rey <mrey@suse.com>"

# Global
cobbler_xml_url = "http://10.161.0.99/cblr/svc/op/autoinstall/system/{0}"


#: The dictionary, used by :class:`logging.config.dictConfig`
#: use it to setup your logging formatters, handlers, and loggers
#: For details, see
# https://docs.python.org/3.4/library/logging.config.html#configuration-dictionary-schema
DEFAULT_LOGGING_DICT = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {'format': '[%(levelname)s] %(name)s: %(message)s'},
    },
    'handlers': {
        'default': {
            'level': 'NOTSET',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        __name__: {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

#: Map verbosity level (int) to log level
LOGLEVELS = {None: logging.WARNING,  # 0
             0: logging.WARNING,
             1: logging.INFO,
             2: logging.DEBUG,
             }

#: Instantiate our logger
log = logging.getLogger(__name__)


def parse(cliargs=None):
    """Parse the command line and return parsed results
    :param list cliargs: Arguments to parse or None (=use sys.argv)
    :return: parsed CLI result
    :rtype: :class:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(description='Validate autoyast XML')
    parsergroup = parser.add_mutually_exclusive_group(required=True)
    parsergroup.add_argument('-u', '--url',
                        action="store_true",
                        default=False,
                        help="use autoyast XML from URL"
                             " (default: %(default)s)",
                        )
    parsergroup.add_argument('-m', '--machine',
                        action="store_true",
                        default=False,
                        help="use autoyast XML from machine"
                             " (default: %(default)s)",
                        )
    parsergroup.add_argument('-f', '--file',
                        action="store_true",
                        default=False,
                        help="Use autoyast XML from file"
                             " (default: %(default)s)",
                        )
    parser.add_argument('-v', '--verbose',
                        action="count",
                        help="raise verbosity level",
                        )

    parser.add_argument('string',
                        metavar="STRING",
                        help="string that locates autoyast XML",
                        )
    args = parser.parse_args(cliargs)

    # Setup logging and the log level according to the "-v" option
    dictConfig(DEFAULT_LOGGING_DICT)
    log.setLevel(LOGLEVELS.get(args.verbose, logging.DEBUG))
    log.debug("CLI args: %s", args)
    return args


def get_content_from_url(url):
    f = urlopen(url)
    content = f.read()
    return content


def get_xml(args):
    xml = None
    
    if args.url:
        xml = get_content_from_url(args.string)
    elif args.machine:
        xml = get_content_from_url(cobbler_xml_url.format(getfqdn(args.string)))
    elif args.file:
        with open(args.string) as xml_file:
            xml = xml_file.read()
    else:
        # TODO: Recognize which flag to use automagically
        log.error("No flag set. Please set a flag state hiw to parse the input")
        
    return xml


def validate_xml():
    """
    TODO: run jing and xmllint to check xml for errors
    """
    pass


if __name__ == "__main__":
    returncode = 0
    args = parse()
    try:
        print(get_xml(args))
        
    except IOError as err:
        log.error(f"Error: {err}")
        returncode = 1

    sys.exit(returncode)

# EOF
