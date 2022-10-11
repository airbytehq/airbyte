#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
from dataclasses import InitVar, dataclass
from html.parser import HTMLParser
from typing import Any, Mapping
from typing import List

import requests
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


class TrustpilotReviewsParser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.__inside_reviews_script = False
        self.__reviews_script_data = None

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            attrs_map = {e[0]: e[1] for e in attrs}
            if (('type' in attrs_map) and (attrs_map['type'] == 'application/ld+json')) and \
                    (('data-business-unit-json-ld' in attrs_map) and (attrs_map['data-business-unit-json-ld'] == 'true')):
                self.__inside_reviews_script = True

    def handle_data(self, data):
        if self.__inside_reviews_script:
            self.__reviews_script_data = data

    def handle_endtag(self, tag):
        if tag == 'script':
            if self.__inside_reviews_script:
                self.__inside_reviews_script = False

    def get_reviews_script_data(self):
        return self.__reviews_script_data


@dataclass
class MyExtractor(RecordExtractor):
    options: InitVar[Mapping[str, Any]]

    @staticmethod
    def __parse_html(response: requests.Response) -> List[Record]:
        dom = response.text
        parser = TrustpilotReviewsParser()
        parser.feed(dom)
        data = parser.get_reviews_script_data()
        data = json.loads(data)
        data = data['@graph']
        data = list(filter(lambda e: e.get('@type', '') == 'Review', data))
        return data

    def extract_records(self, response: requests.Response,
                        ) -> List[Record]:
        return self.__parse_html(response)


# Declarative Source
class SourceTrustpilot(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "trustpilot.yaml"})
