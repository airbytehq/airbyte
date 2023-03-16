import traceback


class ErrorFormatter:

    @staticmethod
    def get_stacktrace_as_string(error) -> str:
        return "".join(traceback.TracebackException.from_exception(error).format())
