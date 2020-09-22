# Validate autoyast XML
Use this script to validate autoyast XML config files.

## Setup
1. Install necessary dependencies:
```
zypper install jing libxml2 yast2-schema
```

## Usage

```
usage: validate-autoyastxml.py [-h] (-u | -m | -f) [-c COBBLER] [-p PROFILE] [-v] STRING

Validate autoyast XML

positional arguments:
  STRING                string that locates autoyast XML

optional arguments:
  -h, --help            show this help message and exit
  -u, --url             use autoyast XML from URL (default: False)
  -m, --machine         use autoyast XML from machine (default: False)
  -f, --file            Use autoyast XML from file (default: False)
  -c COBBLER, --cobbler COBBLER
                        Cobbler IP address
  -p PROFILE, --profile PROFILE
                        Path to RELAX NG schema to use to validate XML
  -v, --verbose         Raise verbosity level
```
