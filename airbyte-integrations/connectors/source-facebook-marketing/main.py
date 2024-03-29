#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from gevent import monkey
monkey.patch_all(httplib=True, request=True, thread=False, select=True)

from source_facebook_marketing.run import run


if __name__ == "__main__":
    run()
