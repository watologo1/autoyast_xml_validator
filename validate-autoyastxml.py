#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import logging
import sys
import os
import glob
import types
import tempfile
from logging.config import dictConfig
from socket import getfqdn
from subprocess import PIPE, Popen
from urllib.request import urlopen

# Global
COBBLER_XML_URL  = 'http://{0}/cblr/svc/op/autoinstall/system/{1}'
PROFILE_GLOB     = '/usr/share/YaST2/schema/autoyast/distros/*'
PROFILE_LOCATION = '/usr/share/YaST2/schema/autoyast/distros/{0}/{1}/profile.rng'

#: The dictionary, used by :class:`logging.config.dictConfig`
#: use it to setup your logging formatters, handlers, and loggers
#: For details, see
# https://docs.python.org/3.4/library/logging.config.html#configuration-dictionary-schema
DEFAULT_LOGGING_DICT = types.MappingProxyType(
    {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {'format': '[%(levelname)s]: %(message)s'},
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
    parser = argparse.ArgumentParser(description='Validate autoyast XML')
    parsergroup = parser.add_mutually_exclusive_group(required=True)
    parsergroup.add_argument(
        '-u',
        '--url',
        action='store',
        default=False,
        help='use autoyast XML from URL (default: %(default)s)'
    )
    parsergroup.add_argument(
        '-s',
        '--system',
        action='store',
        default=False,
        help='use autoyast XML from cobbler system (default: %(default)s)'
    )
    parsergroup.add_argument(
        '-f',
        '--file',
        action='store',
        default=False,
        help='Use autoyast XML from file (default: %(default)s)'
    )
    parsergroup.add_argument(
        '-l', '--list', action='store_true', default=False,
        help='Show distros and archs (to be used with -d [ -a ] param) of installed and available XML syntax definitions'
    )

    parser.add_argument(
        '-c',
        '--cobbler',
        action='store',
        help='Cobbler IP address',
        required=False,
    )
    parser.add_argument(
        '-p',
        '--profile',
        action='store',
        default='/usr/share/YaST2/schema/autoyast/rng/profile.rng',
        help='Path to RELAX NG schema to use to validate XML',
        required=False,
    )
    parser.add_argument(
        '-d',
        '--distro',
        action='store',
        default='',
        help='Distro to check validate against, needs yast2-schemas package',
        required=False
    )
    parser.add_argument(
        '-a',
        '--arch',
        action='store',
        default='x86_64',
        help='Distro to check validate against, needs yast2-schemas package',
        required=False
    )
    parser.add_argument(
        '-v', '--verbose', action='count', help='Raise verbosity level'
    )
    parser.add_argument(
        '--save', action='store_true', default=False,
        help='Always store retrieved XML file, not only in error case'
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

def list_distros():

    distro = {}
    distro_folders = glob.glob(PROFILE_GLOB)
    print("\nList of supported distributions and architectures:\n")
    print("Distro")
    print("[ Architectures, ]\n")
    for f in distro_folders:
        archs = []
        arch_folders = glob.glob("%s/*" % f)
        for a in arch_folders:
            archs.append(os.path.basename(a))
        if archs:
            print(os.path.basename(f))
            print(archs)
            print()
            distro[os.path.basename(f)] = archs

def get_rng(args):
    """Get profile.rng file location depending on CLI args.

    :param args: arguments passed to CLI
    :returns: autoyast XML
    :rtype: str

    """
    profile = None

    if not args.distro:
        profile = args.profile
    else:
        profile = PROFILE_LOCATION.format(args.distro, args.arch)
    if not os.path.isfile(profile):
        raise IOError("Cannot locate %s" % profile)
    return profile    

def get_xml(args):
    """Get XML string from different sources, depending on CLI args.

    :param args: arguments passed to CLI
    :returns: autoyast XML
    :rtype: str

    """
    xml = None

    if args.url:
        xml = get_content_from_url(args.url)
    elif args.system:
        url = COBBLER_XML_URL.format(args.cobbler, args.system)
        log.debug('XML content located at URL: %s', url)
        xml = get_content_from_url(url)
    elif args.file:
        with open(args.file) as xml_file:
            xml = xml_file.read()
    else:
        log.error(
            'No autoyast.xml source specified. Use either -u, -f or -c and -s options'
        )
    return xml.strip()


def validate_xml(args, xml, profile):
    """Check xml for errors with xmllint.

    :param args: arguments passed to CLI
    :param xml: autoyast XML as string
    :returns: returns: returns: return if autoyast XML validates
    :rtype: bool

    """
    # check xml syntax with xmllint
    success = True
    log_delim = "---------------------------------------------------------"

    command = ['xmllint', '--noout', '--relaxng', profile, '/dev/stdin']
    process = Popen(
        command,
        stdout=PIPE,
        stderr=PIPE,
        stdin=PIPE
    )
    stdout, stderr = process.communicate(input=xml.encode())
    log.debug('xmllint return code: %d', process.returncode)
    if process.returncode:
        log.warning("xmllint output %s", log_delim)
        log.warning('stderr: %s', str(stderr, encoding='utf-8'))
        log.warning('stdout: %s', str(stdout, encoding='utf-8'))
        log.warning("xmllint output %s", log_delim)
        success = False

    command = ['jing', profile, '/dev/stdin']
    # check RELAX NG schema with jing
    process = Popen(
        command,
        stdout=PIPE,
        stderr=PIPE,
        stdin=PIPE,
    )
    stdout, stderr = process.communicate(input=xml.encode())
    log.debug('jing return code: %d', process.returncode)
    if process.returncode:
        log.warning("jing output    %s", log_delim)
        log.warning('stderr: %s', str(stderr, encoding='utf-8'))
        log.warning('stdout: %s', str(stdout, encoding='utf-8'))
        log.warning("jing output    %s", log_delim)
        success = False

    if not success or args.save:
        temp = tempfile.NamedTemporaryFile(prefix="autoyast_xml_validator_", delete=False)
        temp.write(xml.encode())
        temp.close()
        if not success:
            raise SyntaxError('XML has wrong Syntax. XML file store here: %s' % temp.name)
        else:
            print("XML file stored: %s" % temp.name)

    """
    A returncode of 0 means "good". But the function should return True
    if the XML is valid. As 0 is falsy in Python, bool(0) would return
    False. Thus it is needed to invert the bool with a 'not' to adapt it
    to our needs.
    return True if both checks have a returncode of 0
    """
    return success


if __name__ == '__main__':
    RETURN_CODE = 0
    args = parse()
    try:
        if args.list:
            list_distros()
        else:
            profile = get_rng(args)
            print(profile)
            xml = get_xml(args)
            if not validate_xml(args, xml, profile):
                RETURN_CODE = 99
    except IOError as err:
        log.error('IOError: %s', err)
        RETURN_CODE = 3
    except SyntaxError as err:
        log.error('SyntaxError: %s', err)
        RETURN_CODE = 2
    except Exception:
        log.exception("Unknown Error")
        RETURN_CODE = 1

    sys.exit(RETURN_CODE)

# EOF
