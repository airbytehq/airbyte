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

from typing import Dict, List


def transform_date_fields(
    records: List, key: str = "changeAuditStamps", prop: List = ["created", "lastModified"], field: str = "time"
) -> List:
    """
    The cursor_field has the nested structure as:
    EXAMPLE:
    :: {
        "changeAuditStamps": {
            "created": {
                "time": 1629581275000
            },
            "lastModified": {
                "time": 1629664544760
                }
            }
        }
    We need to unnest this structure based on `dict_key` and `dict_prop` values.
    """
    result = []
    for record in records:
        target_dict: Dict = record.get(key, None)
        if target_dict:
            for p in prop:
                # Update dict with flatten key:value
                record.update(**{p: target_dict.get(p).get(field, None)})
            # Remove nested structure from the data
            record.pop(key)
        result.append(record)
    return result
