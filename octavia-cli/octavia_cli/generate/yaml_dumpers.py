#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import yaml


# This custom Dumper allows the list indentation expected by our prettier formatter:
# Normal dumper behavior
# my_list:
# Custom behavior to match prettier's rules:
# my_list:
class CatalogDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)
