# Validate autoyast XML
Use this script to validate autoyast XML config files.

## Setup
1. Install necessary dependencies: `zypper install jing libxml2 yast2-schema`

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


# Generate YaST 2 schema 
This script extracts the RELAX NG schema files of different OS versions to directory `yast2_schema`. These schema files can then be used to check for validity of autoyast XML configuration files using `validate-autoyastxml.py`.

## Usage

```
./generate_yast2_schema.sh
```

# Test distro autoyast XML
Use this script to deploy different OS versions on a server via cobbler and check for autoyast config XML errors using `validate-autoyastxml.py` and the related RELAX NG schema files.

## Usage
1. Edit the variables in the script if necessary
2. Run the script: `./test_distro_autoyast_xml.sh`
