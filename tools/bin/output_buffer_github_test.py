#!/usr/bin/env python3

import time
import datetime

n = 0
total_size = 0
while True:
    n += 1
    tpl = "{} line number {}, total_size: {}"
    now = datetime.datetime.now()
    s = tpl.format(now, n, total_size)
    total_size += len(s)
    s = tpl.format(now, n, total_size)
    print(s, flush=False)

    if n < 140:
        time.sleep(1)
    else:
        time.sleep(10)
