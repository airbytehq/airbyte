#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import traceback


class ErrorFormatter:

    @staticmethod
    def get_stacktrace_as_string(error) -> str:
        return "".join(traceback.TracebackException.from_exception(error).format())
