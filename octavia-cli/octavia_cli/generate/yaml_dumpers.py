#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import yaml


# This custom Dumper allows the list indentation expected by our prettier formatter:
# Normal dumper behavior
# my_list:
# - bar: test2
#   foo: test
# - bar: test4
#   foo: test3
# Custom behavior to match prettier's rules:
# my_list:
#   - bar: test2
#     foo: test
#   - bar: test4
#     foo: test3
class CatalogDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(CatalogDumper, self).increase_indent(flow, False)
