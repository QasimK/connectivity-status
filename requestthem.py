#!/bin/python3
"""Request websites to see if they are working."""

from contextlib import ExitStack
from datetime import datetime, timezone
from http.client import HTTPException
from time import perf_counter, sleep
from urllib import request
from urllib.error import URLError


# TODO: Flexible time periods depending on page.
TIME_PERIOD = 15 * 60  # 15 minutes

check_pages = [
    ('www.google.co.uk', b'<title>Google</title>'),
    ('www.bbc.co.uk', b'<title>BBC'),
    # Speedtest: 100MB sparse file takes 13s at 60Mb/s
    ('speedtest.tele2.net/100MB.zip', b'\x00' * 100),
]


def time_webpage(url, verify):
    """Return time (microseconds) to download page or None."""
    start = perf_counter()
    try:
        with request.urlopen('http://' + url) as response:
            html = response.read()
    except (HTTPException, URLError, OSError) as err:
        return None
    time_taken = perf_counter() - start

    if response.status != 200 or verify not in html:
        return None

    return time_taken


def main():
    with ExitStack() as stack:
        fouts = {}
        for page, _ in check_pages:
            page_logfile = page.partition('/')[0] + '.log'
            fouts[page] = stack.enter_context(open(page_logfile, 'a'))

        while True:
            for page, verify in check_pages:
                time = time_webpage(page, verify)
                output = '{when} {status}\n'.format(
                    when=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    status='{:.6f}'.format(time) if time else 'DOWN',
                )
                print('{}: {}'.format(page, output), end='')
                fouts[page].write(output)

            sleep(TIME_PERIOD)


if __name__ == '__main__':
    main()
