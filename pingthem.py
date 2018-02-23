#!/bin/python3

import os
import time
from contextlib import ExitStack
from datetime import datetime, timezone


check_hosts = [
    '192.168.1.1',
    '192.168.1.2',
    '8.8.8.8',
    'google.com',
    'bbc.co.uk',
]


def is_it_up(who):
    return os.system('ping -c 1 %s' % who) == 0


def main():
    with ExitStack() as stack:
        fouts = {
            host: stack.enter_context(open(host + '.log', 'a'))
            for host in check_hosts
        }

        while True:
            for host in check_hosts:
                output = '{when} {status}\n'.format(
                    when=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    status='UP' if is_it_up(host) else 'DOWN',
                )
                fouts[host].write(output)

            time.sleep(60)


if __name__ == '__main__':
    main()

