import requests
import json

from abc import ABC, abstractmethod
from airbyte_cdk.logger import AirbyteLogger
from time import sleep
from requests.models import Response

from airbyte_cdk.models import (
    AirbyteMessage,
)

import csv
import xmltodict
from typing import Generator

REQUEST_RETRIES_BEFORE_ERROR = 20


def get_config_as_dict(config: json) -> dict:
    """
    Transform config into a simple dict that can be accessed with ease
    """
    return json.loads(json.dumps(config))


class Adaptive(ABC):
    """
    An abstract class to handle all communication with the adaptive,in addition
    all methods that are not specifically used by one method it is advices to
    be placed here so any future method can reuse the method.
    """

    def __init__(self, logger: AirbyteLogger, config: json):
        self.logger = logger
        self.config = get_config_as_dict(config=config)  # save config in better format

    def _perform_request(self, url, headers, payload) -> Response:
        """
        A Generic method to perform the request, please do not override this
        in theory you should be able to perform different kind of request
        depending on what you want to know. However, the reponse of adaptive
        is of type xml, which means any kind of operation is very difficult
        without parsing the response as a whole xml structure. Several optimization
        could be implemented but reading it as text and parsing the response
        as stream but this will make the code unmantainable. So for adaptive
        it is better to be slow since the load data is not so big.

        In addition, this is the core way to perform the request using the requests
        package. All logic should be enclosed here for easier maintainance
        """

        response = None
        counter = 0
        while response is None:
            counter = counter + 1
            if counter > 1:
                self.logger.warn(f"Perform request try: {counter}")
            try:
                return requests.request("POST", url, timeout=30, headers=headers, data=payload)
            except requests.ConnectionError as e:
                if counter >= REQUEST_RETRIES_BEFORE_ERROR:
                    self.logger.error(f"Tried for {counter} times and something is erronnious, abort...")
                    raise e
                self.logger.warn("Connection error occurred", e)
                sleep(3)
                continue
            except requests.Timeout as e:
                self.logger.warn("Timeout error - request took too long", e)
                sleep(3)
                continue
            except requests.RequestException as e:
                self.logger.warn("General error", e)
                sleep(3)
                continue
            except KeyboardInterrupt:
                self.logger.warn("The program has been canceled")
        return response

    def perform_request(self) -> Generator[Response, None, None]:
        """
        Method to be used when retrieval of all data is needed.
        """
        url = "https://api.adaptiveinsights.com/api/v32"
        headers = {"Content-Type": "application/xml"}

        for payload in self.construct_payload():
            yield self._perform_request(url=url, payload=payload, headers=headers)

    def perform_request_fast(self) -> Response:
        """
        Method to be used when a single call will be made, necessary to identify
        the sucess of the request and/or a data sample that will be fetched.
        """
        url = "https://api.adaptiveinsights.com/api/v32"
        headers = {"Content-Type": "application/xml"}
        payload = self.construct_payload_fast()
        return self._perform_request(url=url, payload=payload, headers=headers)

    def get_data_from_response(self, response: Response):
        return xmltodict.parse(response.content)["response"]["output"]

    def parse_response(self, response: Response):
        return xmltodict.parse(response.content)

    def is_request_successful(self, response: Response):
        return self.parse_response(response=response)["response"]["@success"] == "true"

    def get_request_error_messages(self, response: Response):
        return self.parse_response(response=response)["response"]["messages"]["message"]

    def get_csv_columns_from_response(self, response):
        """
        Assumes that the reponse is of CSV type and only the first row is returned
        which maps to the columns
        """
        data = self.get_data_from_response(response)
        reader = csv.reader(data.split("\n"), delimiter=",", quotechar='"')
        headers = next(reader, None)
        return headers

    def get_csv_data_from_response(self, response):
        """
        Assumes that the reponse is of CSV type, the first row is skipped
        and only the rest of the data is returned
        """
        data = self.get_data_from_response(response)
        csv_data = []
        reader = csv.reader(data.split("\n"), delimiter=",", quotechar='"')
        # skip header
        next(reader, None)
        for row in reader:
            csv_data.append(row)
        return csv_data

    # these four methods MUST be implemented by child adaptive classes
    @abstractmethod
    def construct_payload(self) -> Generator[str, None, None]:
        """
        This generator, creates the various payloads that will be made to adaptive
        in order to fetch the data.
        """
        raise NotImplementedError

    @abstractmethod
    def construct_payload_fast(self) -> str:
        """
        This method generates a payload, necessary to perform the handshake
        with the adaptive and/or fetching a sample of data to identify
        data format and such.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_table_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_table_schema(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def generate_table_row(self) -> Generator[AirbyteMessage, None, None]:
        raise NotImplementedError
