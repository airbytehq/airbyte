import re


def is_valid_env_var(var_name: str) -> bool:
    return bool(re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", var_name))
