#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
import re
from typing import Any

import yaml

ENV_VAR_MATCHER_PATTERN = re.compile(r".*\$\{([^}^{]+)\}.*")


def env_var_replacer(loader: yaml.Loader, node: yaml.Node) -> Any:
    """Convert a YAML node to a Python object, expanding variable.

    Args:
        loader (yaml.Loader): Not used
        node (yaml.Node): Yaml node to convert to python object

    Returns:
        Any: Python object with expanded vars.
    """
    return os.path.expandvars(node.value)


class EnvVarLoader(yaml.SafeLoader):
    pass


# All yaml nodes matching the regex will be tagged as !environment_variable.
EnvVarLoader.add_implicit_resolver("!environment_variable", ENV_VAR_MATCHER_PATTERN, None)

# All yaml nodes tagged as !environment_variable will be constructed with the env_var_replacer callback.
EnvVarLoader.add_constructor("!environment_variable", env_var_replacer)
