#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import re

class Helpers:
    
    @staticmethod
    def get_spreadsheet_id(id_or_url: str) -> str:
        if re.match(r"(http://)|(https://)", id_or_url):
            m = re.search(r"(/)([-\w]{40,})([/]?)", id_or_url)
            if m.group(2):
                return m.group(2)
        else:
            return id_or_url
