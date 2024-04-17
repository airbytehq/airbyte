#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from gevent import monkey
monkey.patch_all(httplib=True, request=True, thread=False, select=True)

from source_facebook_marketing.run import run


if __name__ == "__main__":

    from datetime import datetime

    now_start = datetime.now()

    current_time = now_start.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    run()

    now_end = datetime.now()

    current_time = now_end.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    runtime = now_end - now_start
    print("Runtime ", runtime.total_seconds())
