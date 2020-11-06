#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import sys
import types
from logging.config import dictConfig
from socket import getfqdn
from subprocess import PIPE, run
from urllib.request import urlopen

# Global
COBBLER_XML_URL = 'http://{0}/cblr/svc/op/autoinstall/system/{1}'

#: The dictionary, used by :class:`logging.config.dictConfig`
#: use it to setup your logging formatters, handlers, and loggers
#: For details, see
# https://docs.python.org/3.4/library/logging.config.html#configuration-dictionary-schema
DEFAULT_LOGGING_DICT = types.MappingProxyType(
    {
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
                'propagate': True,
            },
        },
    }
)

#: Map verbosity level (int) to log level
LOGLEVELS = types.MappingProxyType({
    None: logging.WARNING,  # 0
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
})

#: Instantiate our logger
log = logging.getLogger(__name__)


def parse(cliargs=None):
    """Parse the command line and return parsed results.

    :param cliargs: Arguments to parse or None (=use sys.argv) (Default value = None)
    :returns: parsed CLI result
    :rtype: class:`argparse.Namespace`

    """
    parser = argparse.ArgumentParser(description='Validate AutoYaST XML')
    parsergroup = parser.add_mutually_exclusive_group(required=True)
    parsergroup.add_argument(
        '-u',
        '--url',
        action='store_true',
        default=False,
        help='Use AutoYaST XML from URL (default: %(default)s)',
    )
   
    parsergroup.add_argument(
        '-f',
        '--file',
        action='store_true',
        default=False,
        help='Use AutoYaST XML from file (default: %(default)s)',
    )
    parser.add_argument(
        '-o',
        '--output',
        action='store',
        default=False,
        help="File path where downloaded file from url is saved  (default: %(default)s)",
    )
    parser.add_argument(
        '-p',
        '--profile',
        action='store',
        help='Path to RELAX NG schema to use to validate XML',
        required=True,
    )
    parser.add_argument(
        '-v', '--verbose', action='count', help='Raise verbosity level',
    )
    parser.add_argument(
        'string', metavar='STRING', help='string that locates AutoYaST XML',
    )
    args = parser.parse_args(cliargs)

    # Setup logging and the log level according to the '-v' option
    dictConfig(DEFAULT_LOGGING_DICT)
    log.setLevel(LOGLEVELS.get(args.verbose, logging.DEBUG))
    log.debug('CLI args: %s', args)
    return args


def get_content_from_url(url):
    """Get content of a website and return it.

    :param url: URL to get content from
    :returns: content of URL
    :rtype: bool

    """
    with urlopen(url) as xml_site:
        site_content = xml_site.read().decode('utf-8')
    return site_content


def process_xml(args):
    """Get XML string from different soruces, depending on CLI args.

    :param args: arguments passed to CLI
    :returns: AutoYaST XML
    :rtype: str

    """
    xml = None

    if args.url:
        xml = get_content_from_url(args.string)
    elif args.file:
        with open(args.string) as input_xml_file:
            xml = input_xml_file.read()
            
    if args.output:
        with open(args.output, "w") as output_xml_file:
            output_xml_file.write(xml)
        if not xml:
            log.debug("passed XML content is empty!")

    return xml.strip()


def validate_xml(args, xml):
    """Check xml for errors with xmllint.

    :param args: arguments passed to CLI
    :param xml: AutoYaST XML as string
    :returns: returns: returns: return if AutoYaST XML validates
    :rtype: bool

    """
    # check xml syntax with xmllint
    process_xmllint = run(
        ['xmllint', '--noout', '--relaxng', args.profile, '/dev/stdin'],
        stdout=PIPE,
        stderr=PIPE,
        input=xml,
        text=True,
    )
    log.debug('xmllint return code: %s', process_xmllint.returncode)
    if output_xmllint := process_xmllint.stderr.strip():  # xmllint outputs its errors to stderr
        log.debug('xmllint stderr: %s', output_xmllint)

    # check RELAX NG schema with jing
    process_jing = run(
        ['jing', args.profile, '/dev/stdin'],
        stdout=PIPE,
        stderr=PIPE,
        input=xml,
        text=True,
    )
    log.debug('jing return code: %s', process_jing.returncode)
    if output_jing := process_jing.stdout.strip():   # jing outputs its errors to stdout
        log.debug('jing stdout: %s', output_jing)

    # A returncode of 0 means "good". But the function should return True
    # if the XML is valid. As 0 is falsy in Python, bool(0) would return
    # False. Thus it is needed to invert the bool with a 'not' to adapt it
    # to our needs.
    # return True if both checks have a returncode of 0
    successfully_validated = not (process_xmllint.returncode or process_jing.returncode)
    return successfully_validated


if __name__ == '__main__':
    RETURN_CODE = 0
    args = parse()
    try:
        xml = process_xml(args)
        if not validate_xml(args, xml):
            if args.output:
                raise SyntaxError('XML has wrong syntax. Please check the output file: {0}'.format(args.output))
            else:
                raise SyntaxError('XML has wrong syntax.')
    except IOError as err:
        log.debug('IOError: %s', err)
        RETURN_CODE = 3
    except SyntaxError as err:
        log.info('SyntaxError: %s', err)
        RETURN_CODE = 2
    except Exception:
        RETURN_CODE = 1

    sys.exit(RETURN_CODE)
# EOF
