import sys
import getpass
import os

import segment.analytics as analytics

analytics.write_key = 'ER8EjdRVFut7n05XPaaTKrSEnjLscyKr'
analytics.send = True
analytics.debug = True

def _is_airbyte_user():
    return os.getenv("AIRBYTE_ROLE") == "airbyter"

def track_command(f):
    """
    Decorator to track CLI commands with segment.io
    """
    def wrapper(*args, **kwargs):
        ctx = args[0]
        top_level_command = ctx.command_path
        full_cmd = " ".join(sys.argv)

        sys_user_name = getpass.getuser()
        airbyter = _is_airbyte_user()

        # remove anything prior to the command name f.__name__
        # to avoid logging inline secrets
        santized_cmd = full_cmd[full_cmd.find(top_level_command):]

        is_local = kwargs.get('is_local', False)
        user_id = 'local-user' if is_local else 'ci-user'
        event = f"airbyte-ci:{f.__name__}"

        # IMPORTANT! do not log kwargs as they may contain secrets
        analytics.track(user_id, event, {'username': sys_user_name, 'command': santized_cmd, 'airbyter': airbyter})

        return f(*args, **kwargs)
    return wrapper
