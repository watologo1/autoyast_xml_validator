# autoyast-xml-validate 1 2021-07-06 GNU

## NAME

autoyast-xml-validate 

## SYNOPSIS

autoyast-xml-validate (-u URL | -s SYSTEM -c COBBLER | -f FILE) [-p PROFILE | -d DISTRO [ -a ARCH ] ] [-v] [-h] [--save]
autoyast-xml-validate (-u URL | -f FILE | -c COBBLER  ( -s COBBLER_SYSTEM | -p COBBLER_PROFILE ) | -l) [-r PROFILE_RNG] [-P PRODUCT] [-a ARCH] [--save] [-v]

## DESCRIPTION

Use this script to validate autoyast XML config files.

The XML syntax (profile.rng) to check against is specified via -p or -d parameter.

If none is given /usr/share/YaST2/schema/autoyast/rng/profile.rng is used (part of yast2-schema package)

## OPTIONS

  LOCATE AUTOYAST XML FILE WHICH GETS SYNTAX CHECKED (one is mandatory):

  -u URL, --url URL
                        Use autoyast XML from URL (default: False)
  -f FILE, --file FILE
                        Use autoyast XML from file (default: False)
  -s SYSTEM, --system SYSTEM
                        Use autoyast XML from machine (default: False)
			Needs --cobbler
  -p PROFILE, --profile PROFILE
                        Use autoyast XML from cobbler profile (default: False)
			Needs --cobbler
  -c COBBLER, --cobbler COBBLER
                        Cobbler IP address
			Needs --system or --profile


  LOCATE XML AUTOYAST DEFINITIONS (profile.rng):
  (default: /usr/share/YaST2/schema/autoyast/rng/profile.rng)
  
  -r PROFILE_RNG, --profile-rng PROFILE_RNG
                        Path to RELAX NG schema to use to validate XML (profile.rng)
  -P PRODUCT, --product PRODUCT
                        Distribution specific XML syntax to check against
                        This needs yast2-schemas package installed
                        (by default uses x86_64 installed architecture specific
                        XML declarations)
  -a ARCH, --arch ARCH
                        Needs --distro parameter
                        Chose a different architecture XML definition
                        (default x86_64)

  -l, --list
                        Show products and archs (to be used with -P [ -a ] param)
                        of installed and available XML syntax definitions

  --save
                        Always store retrieved XML file, not only in error case.
			Especially useful if autoyast.xml is retrieved via -u URL
			or cobbler parameters. The file can be further edited or
			worked on, also if syntax check was successful.


  -h, --help            show this help message and exit
  -v, --verbose         Raise verbosity level


## RETURN VALUE

```
0:  Successful XML validation
1:  Unknown error
2:  Syntax error
3:  IO error
99: XML validation failed
```

## ENVIRONMENT

Dependencies to other packages:

jing libxml2 yast2-schema yast2-schemas

## FILES

/usr/share/YaST2/schema/autoyast/rng/* (installed by yast2-schema)

/usr/share/YaST2/schema/autoyast/distros/{tw,leap15.3,sle-15-sp3,..}/{x86_64,aarch64,...}/rng/*
(installed by yast2-schemas)

## EXAMPLES

```autoyast-xml-validate -f /tmp/autoyast.xml```

Local autoyast.xml check - Check against a local XML file  
(using rng files from locally installed yast2-schema package)


```autoyast-xml-validate -c cobbler.arch.suse.de -m zinfandel-4.arch.suse.de --save```

cobbler generated autoyast.xml check  
Download and validate against a cobbler generated autoyast.xml

-> this ends up in this URL:  
http://cobbler.arch.suse.de/cblr/svc/op/autoinstall/system/zinfandel-4.arch.suse.de  
-> --save option will store the downloaded autoyast.xml file locally as well for  
   further debugging or development.


```autoyast-xml-validate -c cobbler.arch.suse.de -m zinfandel-4.arch.suse.de -d sle-15-sp3 -a aarch64```

cobbler generated autoyast.xml SLE 15 SP3 aarch64 check:  
Download and validate against a cobbler generated autoyast.xml using SLE 15 SP3  
aarch64 XML definitions

```autoyast-xml-validate -f /tmp/autoyast_xml_validator__di2jtqv -d sle-15-sp3 -a ppc64le```

Validate (probably previously with --save param downloaded) autoyast file against  
sle-15-sp3/ppc64le XML syntax correctness.

```autoyast-xml-validate --list```

List all available distros and their XML (profile.rng) definitions found on disk

# SEE ALSO

jing(1), xmllint(1)
