__all__ = ["is_digit", "is_letter", "is_name_start", "is_name_continue"]

try:
    "string".isascii()
except AttributeError:  # Python < 3.7

    def is_digit(char: str) -> bool:
        """Check whether char is a digit

        For internal use by the lexer only.
        """
        return "0" <= char <= "9"

    def is_letter(char: str) -> bool:
        """Check whether char is a plain ASCII letter

        For internal use by the lexer only.
        """
        return "a" <= char <= "z" or "A" <= char <= "Z"

    def is_name_start(char: str) -> bool:
        """Check whether char is allowed at the beginning of a GraphQL name

        For internal use by the lexer only.
        """
        return "a" <= char <= "z" or "A" <= char <= "Z" or char == "_"

    def is_name_continue(char: str) -> bool:
        """Check whether char is allowed in the continuation of a GraphQL name

        For internal use by the lexer only.
        """
        return (
            "a" <= char <= "z"
            or "A" <= char <= "Z"
            or "0" <= char <= "9"
            or char == "_"
        )

else:

    def is_digit(char: str) -> bool:
        """Check whether char is a digit

        For internal use by the lexer only.
        """
        return char.isascii() and char.isdigit()

    def is_letter(char: str) -> bool:
        """Check whether char is a plain ASCII letter

        For internal use by the lexer only.
        """
        return char.isascii() and char.isalpha()

    def is_name_start(char: str) -> bool:
        """Check whether char is allowed at the beginning of a GraphQL name

        For internal use by the lexer only.
        """
        return char.isascii() and (char.isalpha() or char == "_")

    def is_name_continue(char: str) -> bool:
        """Check whether char is allowed in the continuation of a GraphQL name

        For internal use by the lexer only.
        """
        return char.isascii() and (char.isalnum() or char == "_")
