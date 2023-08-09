#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import traceback


def format_exception(exception: Exception) -> None:
    return str(exception) + "\n" + "".join(traceback.TracebackException.from_exception(exception).format())
