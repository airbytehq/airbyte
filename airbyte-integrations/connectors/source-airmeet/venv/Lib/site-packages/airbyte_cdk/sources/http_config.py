#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

# The goal of this variable is to make an implicit dependency explicit. As part of of the Concurrent CDK work, we are facing a situation
# where the connection pool size is too small to serve all the threads (see https://github.com/airbytehq/airbyte/issues/32072). In
# order to fix that, we will increase the requests library pool_maxsize. As there are many pieces of code that sets a requests.Session, we
# are creating this variable here so that a change in one affects the other. This can be removed once we merge how we do HTTP requests in
# one piece of code or once we make connection pool size configurable for each piece of code
MAX_CONNECTION_POOL_SIZE = 20
