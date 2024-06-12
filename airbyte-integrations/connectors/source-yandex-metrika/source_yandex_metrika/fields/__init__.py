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
        fields_to_replace: set[str] = {self.field_name}
        while fields_to_replace:
            field = fields_to_replace.pop()
            found_replace: bool = False

            for replace_key, format_func in format_funcs.items():
                if replace_key in field:
                    fields_to_replace.update(format_func(field))
                    found_replace = True
            if not found_replace:
                res.append(field)

        return res


class YandexMetrikaFieldsManager:
    """Stores all configured fields"""

    def __init__(self, fields: list[YandexMetrikaSourceField]):
        self.fields: list[YandexMetrikaSourceField] = fields

    def field_lookup(self, field_name: str) -> str | None:
        """Find field name is it is supported"""
        for pattern, pattern_field_type in self.fields:
            if re.match(pattern, field_name):
                return pattern_field_type
        return None

    def prepare_fields_list(self) -> list[tuple[str, str]]:
        """Get list of all processed fields with required types"""
        res: list[tuple[str, str]] = []
        for field in self.fields:
            res.extend([(variant, field.field_type) for variant in field.variants()])

        return res

    def get_all_fields(self) -> list[YandexMetrikaSourceField]:
        return self.fields

    def get_all_fields_values(self) -> list[str]:
        res: list[str] = []
        for field in self.fields:
            res.extend(field.variants())
        return res

    def get_required_fields(self) -> list[YandexMetrikaSourceField]:
        return [field for field in self.fields if field.required]

    def get_required_fields_names(self) -> list[str]:
        return [field.field_name for field in self.get_required_fields()]
