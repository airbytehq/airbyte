#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from datetime import datetime

STRING_TYPES = [
    "string",
    "email",
    "reference",
    "url",
    "phone",
    "textarea",
    "text",
    "lead_function",
]


def to_datetime_str(date: datetime) -> str:
    """
    Returns the formated datetime string.
    :: Output example: '2021-07-15T0:0:0Z' FORMAT : "%Y-%m-%dT%H:%M:%SZ"
    """
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def clean_string(string: str) -> str:
    """
    input -> output
    "updatedAt" -> "updated_at"
    "UpdatedAt" -> "updated_at"
    "base URL" -> "base_url"
    "UPdatedAt" -> "u_pdated_at"
    "updated_at" -> "updated_at"
    " updated_at " -> "updated_at"
    "updatedat" -> "updatedat"
    """

    abbreviations = ("URL", "GUID", "IP")
    if any(map(lambda w: w in string, abbreviations)):
        return string.lower().replace(" ", "_")
    return "".join("_" + c.lower() if c.isupper() else c for c in string if c != " ").strip("_")


def format_value(value, schema):
    if not isinstance(schema["type"], list):
        field_type = [schema["type"]]
    else:
        field_type = schema["type"]

    if value in [None, "", "null"]:
        return None
    elif "integer" in field_type:
        if isinstance(value, int):
            return value

        # Custom Marketo percent type fields can have decimals, so we drop them
        decimal_index = value.find(".")
        if decimal_index > 0:
            value = value[:decimal_index]
        return int(value)
    elif "string" in field_type:
        return str(value)
    elif "number" in field_type:
        return float(value)
    elif "boolean" in field_type:
        if isinstance(value, bool):
            return value
        return value.lower() == "true"

    return value
