import re
from typing import Callable


attribution_values: list[str] = [
    "first",
    "last",
    "lastsign",
    "last_yandex_direct_click",
    "cross_device_first",
    "cross_device_last",
    "cross_device_last_significant",
    "cross_device_last_yandex_direct_click",
    "automatic",
]

group_values: list[str] = ["day", "week", "month", "quarter", "year"]

currency_values: list[str] = ["RUB", "USD", "EUR", "YND"]

"""
Format functions create all required fields with real values
Can replace id with real value (on later steps), create fields for all currencies and so on
"""

format_funcs: dict[str, Callable[[str], list[str]]] = {
    "<attribution>": lambda field_name: [field_name.replace("<attribution>", attribution) for attribution in attribution_values],
    "<goal_id>": lambda field_name: [field_name.replace("<goal_id>", "\d+")],
    "<group>": lambda field_name: [field_name.replace("<group>", group) for group in group_values],
    "<experiment_ab>": lambda field_name: [field_name.replace("<experiment_ab>", "\d+")],
    "<currency>": lambda field_name: [field_name.replace("<currency>", currency) for currency in currency_values],
}


class YandexMetrikaSourceField:
    """Field for yandex metrika source"""

    def __init__(self, field_name: str, field_type: str, required: bool = False):
        self.field_name: str = field_name
        self.field_type: str = field_type
        self.required: bool = required

    def variants(self) -> list[str]:
        """
        Get all variants of this field
        Example: field<currency> -> fieldUSD, fieldRUB, ...
        """
        res: list[str] = []
        while any([replace_key in self.field_name for replace_key in format_funcs.keys()]):
            replace_key, format_func = [(key, func) for key, func in format_funcs.items() if key in self.field_name][0]
            res.extend(format_func(self.field_name))

        return res


class YandexMetrikaFieldManager:
    """Stores all configured fields"""

    def __init__(self, fields: list[YandexMetrikaSourceField]):
        self.fields: list[YandexMetrikaSourceField] = fields

    def field_lookup(self, field_name: str) -> str | None:
        """Find field name is it is supported"""
        for pattern, pattern_field_type in self.fields:
            if re.match(pattern, field_name):
                return pattern_field_type
        return None


def prepare_fields_list(fields_list) -> tuple[list[str | tuple[str, str]], list[str]]:
    """Create list of processed fields with replaced <> sequences (like goal_id)"""
    prepared_fields_list: list[str | tuple[str, str]] = []
    original_fields_list: list[str] = []
    for field in fields_list:
        field_name, field_type = field if isinstance(field, tuple) else field, "string"

        original_fields_list.append(field_name)
        while any([replace_key in field_name for replace_key in format_funcs]):
            replace_key, format_func = [(key, func) for key, func in format_funcs.items() if key in field_name][0]
            if isinstance(field, tuple):
                prepared_fields_list += [(formatted_name, field_type) for formatted_name in format_func(field_name)]
            else:
                prepared_fields_list += format_func(field_name)

    return prepared_fields_list, original_fields_list


def field_lookup(field_name: str, list_of_fields: list[tuple]) -> tuple[bool, str | None]:
    for pattern, pattern_field_type in list_of_fields:
        if re.match(pattern, field_name):
            return True, pattern_field_type
    return False, None
