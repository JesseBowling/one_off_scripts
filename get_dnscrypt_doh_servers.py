#!/usr/bin/env python3
# encoding: utf-8
import logging
import urllib3
import argparse
import requests
import validators
import re

urllib3.disable_warnings()

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s[%(lineno)s][%(filename)s] - %(message)s'

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def get_doh_from_dnscrypt():
    url = 'https://download.dnscrypt.info/dnscrypt-resolvers/json/public-resolvers.json'
    headers = {'Accept': 'application/json, text/plain, */*',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
               'Origin': 'https://dnscrypt.info',
               'Sec-Fetch-Site': 'same-site',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Dest': 'empty',
               'Referer': 'https://dnscrypt.info/',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-US,en;q=0.9'
               }
    r = requests.get(url, headers=headers)
    data = r.json()

    return data

def main():

    parser = argparse.ArgumentParser(
        description='Ask DNSCrypt for all the domains that serve DoH or DNSCrypt',
        epilog='http://xkcd.com/353/')
    parser.add_argument('-d', '--debug', action="store_true", dest='debug',
                        default=False,
                        help='Get debug messages about processing')
    parser.add_argument('-i', '--ipv4', action='store_true', dest='ipv4',
                        default=False,
                        help='Output the IPv4 addresses found')
    parser.add_argument('-s', '--ipv6', action='store_true', dest='ipv6',
                        default=False,
                        help='Output the IPv4 addresses found')
    parser.add_argument('-f', '--fqdn', action='store_true', dest='fqdn',
                        default=False,
                        help='Output the domain addresses found')
    options = parser.parse_args()

    if options.debug:
        logger.setLevel(logging.DEBUG)

    data = get_doh_from_dnscrypt()

    fqdn = set()
    ipv4 = set()
    ipv6 = set()

    for item in data:
        if item.get('addrs'):
            for a in item['addrs']:
                a = re.sub('[\[\]]', '', a)
                if validators.domain(a):
                    fqdn.add(a)
                elif validators.ipv4(a):
                    ipv4.add(a)
                elif validators.ipv6(a):
                    ipv6.add(a)
                else:
                    logger.debug('Ignoring address: {}'.format(a))

    if options.ipv4:
        for item in ipv4:
            print(item)
    if options.ipv6:
        for item in ipv6:
            print(item)
    if options.fqdn:
        for item in fqdn:
            print(item)

if __name__ == '__main__':
    main()
