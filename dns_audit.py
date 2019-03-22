#!/usr/bin/env python
'''Create compressed, encrypted, signed extract file with Federal CyHy data for integration with the Weathermap project.

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

'''

import dns.resolver
import dns.ttl
import dns.zone
import dns.query
import re
from pprint import pprint
import dns.name
import dns.message
import dns.query
import dns.flags
import dns.exception
import socket
from docopt import docopt
import yaml
import datetime
from pymongo import MongoClient
from tqdm import tqdm

record_types = ['NS', 'A', 'MX', 'SOA']
DB_CONFIG_FILE = 'mongo_config.yaml'

def dns_query(domain, mongo_config):

    for record in record_types:
        try:
            reply = dns.resolver.query(dns.name.from_text(domain), record, tcp=True)
            if record == 'NS':
                # Use Authoritive name servers for resolvers
                my_resolver = dns.resolver.Resolver()
                # Set resolvers to empty list
                my_resolver.nameservers = []
                # Append each authoritative names servers to the list of resolvers
                for auth in reply.rrset:
                    # Query the domain to the Authoritive name server
                    my_resolver.nameservers.append(socket.gethostbyname(auth.to_text()))
                answer = my_resolver.query(domain)
                if mongo_config:
                    ns_dns_reply_to_mongo(domain, reply, answer, mongo_config)
                else:
                    print('Domain {} {} record(s) are {} with ttl {}'.format(domain, record, [str(response) for response in reply], answer.ttl))
            elif record == 'SOA':
                if mongo_config:
                    soa_dns_reply_to_mongo(domain, reply, mongo_config)
                else:
                    print('Domain {} {} record(s) are {}'.format(domain, record, [str(response) for response in reply]))
            elif record == 'A':
                if mongo_config:
                    a_dns_reply_to_mongo(domain, reply, mongo_config)
                else:
                    print('Domain {} {} record(s) are {} with ttl {}'.format(domain, record, [str(response) for response in reply], reply.ttl))
            elif record == 'MX':
                if mongo_config:
                    mx_dns_reply_to_mongo(domain, reply, mongo_config)
                else:
                    print('Domain {} {} record(s) are {} '.format(domain, record, [str(response) for response in reply]))
        # except (dns.resolver.NoAnswer, dns.exception.Timeout) as e:
        #     print('Error occured: ' + str(e))
        except Exception as e:
            print('An error occured on domain: {} \nFor record type: {}\n Error: {}'.format(domain, record,e))

def ns_dns_reply_to_mongo(domain, reply, name_server_answer, mongo_config):
    db = db_from_config(mongo_config) # set up database connection
    db.ns_records.update_one({'domain': domain,
                          'latest': True},
                         {'$set': {'domain': domain,
                          'nameservers': [str(server) for server in reply.rrset],          # List of name servers in NS reply
                          'name_server_ttl': name_server_answer.ttl,                       # TTL of domain from Authoritive Name Server
                          'ip': str(name_server_answer.rrset[0]),                          # IP of domain at namesever
                          'insert_date': datetime.datetime.now().isoformat(),
                          'latest': True
                          }}, upsert=True)

def a_dns_reply_to_mongo(domain, reply, mongo_config):
    db = db_from_config(mongo_config)#db_config_file)  # set up database connection
    # A record
    db.a_records.update_one({'domain': domain,
                         'latest': True},
                        {'$set': {'domain': domain,
                        'ttl': reply.ttl,
                        'ip': str(reply.rrset[0]),
                        'insert_date': datetime.datetime.now().isoformat(),
                        'latest': True
                        }}, upsert=True)

def mx_dns_reply_to_mongo(domain, reply, mongo_config):
    db = db_from_config(mongo_config)  # set up database connection
    # MX record
    db.mx_records.update_one({'domain': domain,
                          'latest': True},
                         {'$set': {'domain': domain,
                          'ttl': reply.ttl,
                          'priority': reply.rrset[0].preference,
                          'mx_domain': str(reply.rrset[0].exchange),
                          'insert_date': datetime.datetime.now().isoformat(),
                          'latest': True
                          }}, upsert=True)

def soa_dns_reply_to_mongo(domain, reply, mongo_config):
    db = db_from_config(mongo_config)  # set up database connection
    # SOA record
    db.soa_records.update_one({'domain': domain,
                               'latest': True},
                              {'$set': {'domain': domain,
                               'serial': reply[0].serial,
                               'tech': str(reply[0].rname),
                               'refresh': reply[0].refresh,
                               'retry': reply[0].retry,
                               'expire': reply[0].expire,
                               'minimum': reply[0].minimum,
                               'mname':str(reply[0].mname),
                               'insert_date': datetime.datetime.now().isoformat(),
                               'latest': True
                               }}, upsert=True)
                               
def db_from_config(config_filename):
    with open(config_filename, 'r') as stream:
        config = yaml.load(stream)

    try:
        db_uri = config['database']['uri']
        db_name = config['database']['name']
    except:
        print('Incorrect database config file format: {}'.format(config_filename))

    db_connection = MongoClient(db_uri)
    db = db_connection[db_name]
    return db

def main():
    global __doc__
    __doc__ = re.sub('COMMAND_NAME', __file__, __doc__)
    args = docopt(__doc__, version='v0.0.1')
    print(args['--mongo_config'])
    print(args)
    if args['--domain']:
        dns_query(args['--domain'].lower(), args['MONGO_CONFIG'])
    elif args['-f']:
        with open(args['-f']) as file:
            with tqdm(total=len(file.read().split())) as pbar:                  # Set up progress bar
                file.seek(0)
                for domain in file:
                    dns_query(domain.strip().lower(), args['MONGO_CONFIG'])
                    pbar.update(1)                                              # Increment progress bar


if __name__=='__main__':
    main()
