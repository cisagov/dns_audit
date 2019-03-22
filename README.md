# dns_audit :mag_right:

dns_audit tests a domain or list of domains for NS, A, MX, and SOA records

## Getting Started ##

'dns_audit' uses python3

### dns_audit Usage and Examples ###

```bash
python dns_audit.py -d example.com
python dns_audit.py -f domain.txt
python dns_audit.py -d example.com --mongo_config config.yaml
python dns_audit.py -f domain.txt --mongo_config config.yaml
```

#### dns_audit Options ####

```bash
Gets NS, A, MX, and SOA records for a domain and prints them to stdout or imports them to mongo

Usage:
  COMMAND_NAME (-d DOMAIN | -f CSV_FILE) [--mongo_config MONGO_CONFIG]
  COMMAND_NAME (-h | --help)
  COMMAND_NAME --version

Options:
  -h --help                                                         Show this screen
  --version                                                         Show version
  -d DOMAIN --domain=DOMAIN                                         Domain you want to query
  -f DOMAIN_LIST   --file=DOMAIN_LIST                               Name of file containing a list of domains
  -m MONGO_CONFIG  --mongo_config=MONGO_CONFIG                      Export results to mongo

```

## Public Domain ##

This project is in the worldwide [public domain](LICENSE.md).

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain
dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
