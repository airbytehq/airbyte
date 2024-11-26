from typing import Optional, Sequence

__all__ = ["did_you_mean"]

MAX_LENGTH = 5


def did_you_mean(suggestions: Sequence[str], sub_message: Optional[str] = None) -> str:
    """Given [ A, B, C ] return ' Did you mean A, B, or C?'"""
    if not suggestions or not MAX_LENGTH:
        return ""
    parts = [" Did you mean "]
    if sub_message:
        parts.extend([sub_message, " "])
    suggestions = suggestions[:MAX_LENGTH]
    n = len(suggestions)
    if n == 1:
        parts.append(f"'{suggestions[0]}'?")
    elif n == 2:
        parts.append(f"'{suggestions[0]}' or '{suggestions[1]}'?")
    else:
        parts.extend(
            [
                ", ".join(f"'{s}'" for s in suggestions[:-1]),
                f", or '{suggestions[-1]}'?",
            ]
        )
    return "".join(parts)
