import json
import os
from typing import Any

from genson import SchemaBuilder

all_data: dict[str, list[dict[str, Any]]] = {}


def clean_schema(obj, bad_keys=["required"]):
    if isinstance(obj, dict):
        keys = list(obj.keys())
        if len(keys) == 1 and "anyOf" in keys:
            # deal with anyOf field
            any_of_list = obj["anyOf"]
            not_null_types = list(filter(lambda o: o.get("type") != "null", any_of_list))
            del obj["anyOf"]
            if len(not_null_types) == 1 and not_null_types[0]["type"] == "array":
                for k, v in not_null_types[0].items():
                    obj[k] = v
            else:
                obj["type"] = "string"

        for key in list(obj.keys()):
            if key in bad_keys:
                del obj[key]
            elif key == "type":
                if obj[key] != "object":
                    if type(obj[key]) == str:
                        # Make every field nullable if it is not
                        if obj[key] == "null":
                            # Make every null field nullable string
                            obj[key] = ["string", "null"]
                        else:
                            obj[key] = [obj[key], "null"]
                    elif type(obj[key]) == list:
                        # Make every multitype field nullable if it is not
                        if "null" not in obj[key]:
                            obj[key].append("null")
                    else:
                        pass
            else:
                clean_schema(obj[key], bad_keys)
    elif isinstance(obj, list):
        for i in obj:
            clean_schema(i)
    else:
        pass


with open("exh.json", "r") as f:
    l_n = 0
    for raw_l in f:
        l_n += 1
        try:
            l = json.loads(raw_l)
        except Exception as e:
            print(f"{l_n} line:", raw_l)
            continue
        if l["type"] != "RECORD":
            continue
        record = l["record"]
        stream_name = record["stream"]
        try:
            data = record["data"]
        except:
            print(f"{l_n} line:", raw_l)
            continue
        if stream_name not in all_data.keys():
            all_data[stream_name] = []

        all_data[stream_name].append(data)


for stream_name in all_data.keys():
    builder = SchemaBuilder()
    stream_records = all_data[stream_name]
    builder.add_schema({"type": "object", "properties": {}})
    for record in stream_records:
        builder.add_object(record)
    with open(os.path.join("source_vkusvill", "schemas", stream_name + ".json"), "w") as f:
        schema = builder.to_schema()
        clean_schema(schema)
        json.dump(schema, f, indent=2)
