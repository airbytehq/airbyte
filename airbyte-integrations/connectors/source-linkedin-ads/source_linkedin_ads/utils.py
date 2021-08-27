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

from typing import Dict, Iterable, List, Mapping

import pendulum as pdm


def transform_date_fields(
    records: List,
    dict_key: str = "changeAuditStamps",
    props: List = ["created", "lastModified"],
    fields: List = ["time"],
    analytics: bool = False,
) -> Iterable[Mapping]:
    """
    The cursor_field has the nested structure as:
    EXAMPLE:
    :: For Analytics Streams :
        {
            "dateRange": {
                "start": {
                    "month": 8,
                    "day": 13,
                    "year": 2021
                },
                "end": {
                    "month": 8,
                    "day": 13,
                    "year": 2021
                }
            }
        }

    :: For Other Streams:
        {
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
        target_dict: Dict = record.get(dict_key, None)
        if target_dict:
            for prop in props:
                # Update dict with flatten key:value
                for field in fields:
                    # For analytics streams
                    if analytics:
                        record.update(**{f"{prop}.{field}": target_dict.get(prop).get(field, None)})
                    # for All other streams
                    record.update(**{prop: pdm.from_timestamp(target_dict.get(prop).get(field, None) / 1000).to_datetime_string()})
            # For Analytics streams we build `start_date` & `end_date` fields from nested structure.
            if analytics:
                record.update(
                    **{
                        "start_date": pdm.date(record["start.year"], record["start.month"], record["start.day"]).to_date_string(),
                        "end_date": pdm.date(record["end.year"], record["end.month"], record["end.day"]).to_date_string(),
                    }
                )
            # Cleanup the nested structures
            for key in [dict_key, "start.day", "start.month", "start.year", "end.day", "end.month", "end.year", "start", "end"]:
                if key in record.keys():
                    record.pop(key)
        result.append(record)
    return result


def make_slice(records: List, key_value_map: Dict) -> Dict:
    """
    Outputs the Dict with key:value slices for the stream.
    EXAMPLE:
        in: records = [{dict}, {dict}, ...],
            key_value_map = {<slice_key_name>: <key inside record>}
        {
            <slice_key_name> : records.<key inside record>.value,
            ....
        }
    """
    result = {}
    for key in key_value_map:
        value = records[key_value_map.get(key, None)]
        if value:
            result.update(**{key: value})
    return result
