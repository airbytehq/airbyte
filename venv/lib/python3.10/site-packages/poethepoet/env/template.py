import re
from typing import Mapping

_SHELL_VAR_PATTERN = re.compile(
    # Matches shell variable patterns, distinguishing escaped examples (to be ignored)
    # There may be a more direct way to doing this
    r"(?:"
    # $VAR preceded by an odd num of \
    r"(?:[^\\]|^)(?:\\(?:\\{2})*)\$(?P<esc_naked>[\w\d_]+)"
    # ${VAR} preceded by an odd num of \
    r"|(?:[^\\]|^)(?:\\(?:\\{2})*)\$\{(?P<esc_paren>[\w\d_]+)\}"
    # $VAR
    r"|\$(?P<naked>[\w\d_]+)"
    # ${VAR}
    r"|\${(?P<paren>[\w\d_]+)}"
    ")"
)

_SHELL_VAR_PATTERN_BRACES = re.compile(
    # Matches shell variable patterns, distinguishing escaped examples (to be ignored)
    r"(?:"
    # ${VAR} preceded by an odd num of \
    r"(?:[^\\]|^)(?:\\(?:\\{2})*)\$\{(?P<esc_paren>[\w\d_]+)\}"
    # ${VAR}
    r"|\${(?P<paren>[\w\d_]+)}"
    ")"
)


class SpyDict(dict):
    """
    A kind of dict in which the behavior __getitem__ can be overriden.
    """

    def __init__(self, content=tuple(), *, getitem_spy=None):
        super().__init__(content)
        self._getitem_spy = getitem_spy

    def __getitem__(self, key):
        """
        Return a transformed version of the key, and record that it was accessed.
        """
        value = super().__getitem__(key)
        if self._getitem_spy:
            return self._getitem_spy(self, key, value)
        return value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


def apply_envvars_to_template(
    content: str, env: Mapping[str, str], require_braces=False
) -> str:
    """
    Template in ${environmental} $variables from env as if we were in a shell

    Supports escaping of the $ if preceded by an odd number of backslashes, in which
    case the backslash immediately precending the $ is removed. This is an
    intentionally very limited implementation of escaping semantics for the sake of
    usability.
    """
    pattern = _SHELL_VAR_PATTERN_BRACES if require_braces else _SHELL_VAR_PATTERN

    cursor = 0
    resolved_parts = []
    for match in pattern.finditer(content):
        groups = match.groupdict()
        var_name = groups.get("paren") or groups.get("naked")
        escaped_var_name = groups.get("esc_paren") or groups.get("esc_naked")

        if var_name:
            var_value = env.get(var_name)
            resolved_parts.append(content[cursor : match.start()])
            cursor = match.end()
            if var_value is not None:
                resolved_parts.append(var_value)

        elif escaped_var_name:
            # Remove the effective escape char
            resolved_parts.append(content[cursor : match.start()])
            cursor = match.end()
            matched = match.string[match.start() : match.end()]
            if matched[0] == "\\":
                resolved_parts.append(matched[1:])
            else:
                resolved_parts.append(matched[0:1] + matched[2:])

    resolved_parts.append(content[cursor:])
    return "".join(resolved_parts)
