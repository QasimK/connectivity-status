#!/bin/python3
"""Request websites to see if they are working."""

import random
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
from http.client import HTTPException
from time import perf_counter, sleep
from urllib import request
from urllib.error import URLError

from config import LOG_DIR


check_pages = [
    ('www.google.co.uk', b'<title>Google</title>', timedelta(minutes=1)),
    ('www.bbc.co.uk', b'<title>BBC', timedelta(minutes=1)),
    # Speedtest: 100MB sparse file takes 13s at 60Mb/s
    ('speedtest.tele2.net/100MB.zip', 104857600, timedelta(minutes=30)),
    ('ovh.net/files/100Mb.dat', 12500000, timedelta(minutes=30)),
]


def time_webpage(url, verify):
    """Return time (microseconds) to download page or None."""
    start = perf_counter()
    try:
        with request.urlopen('http://' + url, timeout=10) as response:
            html = response.read()
    except (HTTPException, URLError, OSError) as err:
        print(err, flush=True)
        return None
    time_taken = perf_counter() - start

    if response.status != 200 or \
            (isinstance(verify, int) and len(html) != verify) or \
            (isinstance(verify, bytes) and verify not in html):
        return None
    return time_taken


def main():
    with ExitStack() as stack:
        fouts = {}  # Log file for each check
        datetimes = {}  # Last attempt of each check
        for page, _, _ in check_pages:
            page_logfile = page.partition('/')[0] + '.log'
            fouts[page] = stack.enter_context(open(LOG_DIR + page_logfile, 'a'))
            datetimes[page] = datetime.now(timezone.utc) - timedelta(hours=1)

        while True:
            random.shuffle(check_pages)
            for page, verify, time_period in check_pages:
                now = datetime.now(timezone.utc)
                if now - datetimes[page] < time_period:
                    continue

                datetimes[page] = now
                print('{}: '.format(page), end='', flush=True)
                time = time_webpage(page, verify)
                output = '{when} {status}\n'.format(
                    when=now.isoformat().replace('+00:00', 'Z'),
                    status='{:.6f}'.format(time) if time else 'DOWN',
                )
                print('{}'.format(output), end='', flush=True)
                fouts[page].write(output)
                # Do not flush because of poor SD card :(
                # fouts[page].flush()  # NB: specify buffering in file.open instead

                sleep(random.randrange(30, 120))


if __name__ == '__main__':
    main()
