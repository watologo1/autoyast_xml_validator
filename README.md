# Validate autoyast XML
Use this script to validate autoyast XML config files.

## Setup
1. Install necessary dependencies:
```
zypper install jing libxml2 yast2-schema
```

## Usage

```
validate-autoyastxml.py [-h] (-u | -m | -f) [-v] STRING

Validate autoyast XML

positional arguments:
  STRING         string that locates autoyast XML

optional arguments:
  -h, --help     show this help message and exit
  -u, --url      use autoyast XML from URL (default: False)
  -m, --machine  use autoyast XML from machine (default: False)
  -f, --file     Use autoyast XML from file (default: False)
  -v, --verbose  raise verbosity level
```
