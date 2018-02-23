"""Read relevant data."""

import glob
from datetime import datetime


def gather_pings(log_dir='../pingit/'):
    """Return a dict of list of (datetime, success?) keyed by host"""
    hosts = {}
    for filename in glob.glob(log_dir + '*.log'):
        hostname = filename.rstrip('.log').rpartition('/')[2]
        hostinfo = []
        hosts[hostname] = hostinfo
        with open(filename, 'r') as fin:
            for line in fin:
                pingtime, _, status = line.rpartition(' ')
                hostinfo.append((parse_datetime(pingtime), status.strip() == 'UP'))

    return hosts


def gather_requests(log_dir='../requestit/'):
    """Return a list of (datetime, seconds or None)"""


def parse_datetime(string):
    return datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
