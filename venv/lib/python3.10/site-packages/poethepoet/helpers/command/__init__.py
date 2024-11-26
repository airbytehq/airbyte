import re
from glob import escape
from typing import TYPE_CHECKING, Iterator, List, Mapping, Optional, Tuple, cast

if TYPE_CHECKING:
    from .ast import Line, ParseConfig


def parse_poe_cmd(source: str, config: Optional["ParseConfig"] = None):
    from .ast import Glob, ParseConfig, ParseCursor, PythonGlob, Script

    if not config:
        # Poe cmd task content differs from POSIX command lines in that new lines are
        # ignored (except in comments) and glob patterns are constrained to what the
        # python standard library glob module can support
        config = ParseConfig(substitute_nodes={Glob: PythonGlob}, line_seperators=";")

    return Script(ParseCursor.from_string(source), config)


def resolve_command_tokens(
    line: "Line",
    env: Mapping[str, str],
    config: Optional["ParseConfig"] = None,
) -> Iterator[Tuple[str, bool]]:
    """
    Generates a sequence of tokens, and indicates for each whether it includes glob
    patterns that are not escaped or quoted. In case there are glob patterns in the
    token, any escaped glob characters will have been escaped with [].
    """
    from .ast import Glob, ParamExpansion, ParseConfig, PythonGlob

    if not config:
        config = ParseConfig(substitute_nodes={Glob: PythonGlob})

    glob_pattern = re.compile(cast(Glob, config.resolve_node_cls(Glob)).PATTERN)

    def finalize_token(token_parts):
        """
        Determine whether any parts of this token include an active glob.
        If so then apply glob escaping to all other parts.
        Join the result into a single token string.
        """
        includes_glob = any(has_glob for part, has_glob in token_parts)
        token = "".join(
            (
                (escape(token_part) if not has_glob else token_part)
                for token_part, has_glob in token_parts
            )
            if includes_glob
            else (token_part for token_part, _ in token_parts)
        )
        token_parts.clear()
        return (token, includes_glob)

    for word in line:
        # For each token part indicate whether it is a glob
        token_parts: List[Tuple[str, bool]] = []
        for segment in word:
            for element in segment:
                if isinstance(element, ParamExpansion):
                    param_value = env.get(element.param_name, "")
                    if not param_value:
                        continue
                    if segment.is_quoted:
                        token_parts.append((env.get(element.param_name, ""), False))
                    else:
                        # If the the param expansion it not quoted then:
                        # - Whitespace inside a substituted param value results in
                        #  a word break, regardless of quotes or backslashes
                        # - glob patterns should be evaluated

                        if param_value[0].isspace() and token_parts:
                            # param_value starts with a word break
                            yield finalize_token(token_parts)

                        param_words = (
                            (word, bool(glob_pattern.search(word)))
                            for word in param_value.split()
                        )

                        token_parts.append(next(param_words))

                        for param_word in param_words:
                            if token_parts:
                                yield finalize_token(token_parts)
                            token_parts.append(param_word)

                        if param_value[-1].isspace() and token_parts:
                            # param_value ends with a word break
                            yield finalize_token(token_parts)

                elif isinstance(element, Glob):
                    token_parts.append((element.content, True))

                else:
                    token_parts.append((element.content, False))

        if token_parts:
            yield finalize_token(token_parts)
