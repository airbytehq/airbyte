from typing import Dict, List

def transform_date_fields(records: List, key: str ='changeAuditStamps', prop: List = ['created','lastModified'], field: str = "time") -> List:
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