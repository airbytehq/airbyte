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


def make_slice(record: Dict, key_value_map: Dict) -> Dict:
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
        value = record[key_value_map.get(key, None)]
        if value:
            result.update(**{key: value})
    return result


def transform_data(records: List) -> Iterable[Mapping]:
    """
    We need to transform the nested complex data structures into simple key:value pair,
    to be properly normalised in the destination.

    The cursor_field has the nested structure as:
    :: EXAMPLE `dateRange` structure in Analytics streams:
        {
            "dateRange": {
                "start": {"month": 8,"day": 13,"year": 2021},
                "end": {"month": 8,"day": 13,"year": 2021}
            }
        }

    :: EXAMPLE `changeAuditStamps` structure:
        {
            "changeAuditStamps": {
                "created": {"time": 1629581275000},
                "lastModified": {"time": 1629664544760}
            }
        }

    """

    for record in records:

        # Transform `changeAuditStamps`
        if "changeAuditStamps" in record:
            dict_key: str = "changeAuditStamps"
            props: List = ["created", "lastModified"]
            fields: List = ["time"]

            target_dict: Dict = record.get(dict_key, None)
            if target_dict:
                for prop in props:
                    # Update dict with flatten key:value
                    for field in fields:
                        record.update(**{prop: pdm.from_timestamp(target_dict.get(prop).get(field, None) / 1000).to_datetime_string()})
                record.pop(dict_key)

        # Transform `dateRange`
        if "dateRange" in record:
            dict_key: str = "dateRange"
            props: List = ["start", "end"]
            fields: List = ["year", "month", "day"]

            target_dict: Dict = record.get(dict_key, None)
            if target_dict:
                for prop in props:
                    # Update dict with flatten key:value
                    for field in fields:
                        record.update(**{f"{prop}.{field}": target_dict.get(prop).get(field, None)})
                # We build `start_date` & `end_date` fields from nested structure.
                record.update(
                    **{
                        "start_date": pdm.date(record["start.year"], record["start.month"], record["start.day"]).to_date_string(),
                        "end_date": pdm.date(record["end.year"], record["end.month"], record["end.day"]).to_date_string(),
                    }
                )
                # Cleanup tmp fields & nested used parts
                for key in [dict_key, "start.day", "start.month", "start.year", "end.day", "end.month", "end.year", "start", "end"]:
                    if key in record.keys():
                        record.pop(key)

        # Transform `Targeting Criterias`
        if "targetingCriteria" in record:
            targeting_criteria = record.get("targetingCriteria")
            # transform `include`
            if "include" in targeting_criteria.keys():
                and_list = targeting_criteria.get("include").get("and")
                for id, and_criteria in enumerate(and_list):
                    or_dict = and_criteria.get("or")
                    count = 0
                    num = len(or_dict) - 1
                    while count <= num:
                        key = list(or_dict)[count]
                        value = []
                        if isinstance(or_dict[key], list):
                            if isinstance(or_dict[key][0], str):
                                value = or_dict[key]
                            elif isinstance(or_dict[key][0], dict):
                                for v in or_dict[key]:
                                    value.append(v)
                        elif isinstance(or_dict[key], dict):
                            value.append(or_dict[key])
                        # Replace the 'or' with {type:value}
                        record["targetingCriteria"]["include"]["and"][id]["type"] = key
                        record["targetingCriteria"]["include"]["and"][id]["values"] = value
                        record["targetingCriteria"]["include"]["and"][id].pop("or")
                        count = count + 1

            # transform `exclude` if present
            if "exclude" in targeting_criteria.keys():
                or_dict = targeting_criteria.get("exclude").get("or")
                updated_exclude = {"or": []}
                count = 0
                num = len(or_dict) - 1
                while count <= num:
                    key = list(or_dict)[count]
                    value = []
                    if isinstance(or_dict[key], list):
                        if isinstance(or_dict[key][0], str):
                            value = or_dict[key]
                        elif isinstance(or_dict[key][0], dict):
                            for v in or_dict[key]:
                                value.append(v)
                    elif isinstance(or_dict[key], dict):
                        value.append(or_dict[key])
                    updated_exclude["or"].append({"type": key, "values": value})
                    count = count + 1
                record["targetingCriteria"]["exclude"].update(**updated_exclude)

        # tranform `variables` if present
        if "variables" in record:
            variables = record.get("variables").get("data")
            count = 0
            num = len(variables) - 1
            while count <= num:
                key = list(variables)[count]
                params = variables.get(key)
                record["variables"]["type"] = key
                record["variables"]["values"] = []

                count2 = 0
                pnum = len(params) - 1
                while count2 <= pnum:
                    param_key = list(params)[count2]
                    param_value = params.get(param_key)
                    record["variables"]["values"].append({"key": param_key, "value": param_value})
                    count2 = count2 + 1

                record["variables"].pop("data")
                count = count + 1

    yield from records
