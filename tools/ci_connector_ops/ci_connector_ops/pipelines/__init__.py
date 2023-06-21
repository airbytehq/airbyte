#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""The pipelines package."""
import logging

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
