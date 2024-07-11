import re

# Spec from https://github.com/palantir/resource-identifier
def is_valid_rid(ri_string: str) -> bool:
    service_pattern = r'[a-z][a-z0-9\-]*'
    instance_pattern = r'([a-z0-9][a-z0-9\-]*)?'
    type_pattern = r'[a-z][a-z0-9\-]*'
    locator_pattern = r'[a-zA-Z0-9\-\._]+'

    full_pattern = r'^ri\.' + service_pattern + r'\.' + instance_pattern + r'\.' + type_pattern + r'\.' + locator_pattern + r'$'

    return bool(re.match(full_pattern, ri_string))
