#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Iterator

import requests
import pendulum
import xmltodict
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


class DentclinicStaticStream(HttpStream, ABC):
    """Base stream"""
    primary_key = None
    static_endpoint = None
    endpoint_data_path = None
    url_base = "https://dcm-nhn.dentclinicmanager.com/API/DCMConnect.asmx?WSDL"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.api_key = config.get("api_key")

    def get_api_key(self):
        return self.api_key

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {'Content-Type': 'application/soap+xml; charset=utf-8'}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_body_data(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return f"""<?xml version="1.0" encoding="utf-8"?>
            <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
                <soap12:Body>
                    <{self.static_endpoint} xmlns="http://tempuri.org/">
                        <key>{self.api_key}</key>
                    </{self.static_endpoint}>
                </soap12:Body>
            </soap12:Envelope>
        """

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """

        path = self.endpoint_data_path
        data = xmltodict.parse(response.text).copy()
        for key in path:
            data = data.get(key)
            if data is None:
                data = []
                break

        if type(data) == dict:
            data = [data]

        yield from data

# Basic full refresh stream


class DentclinicVisidIdStream(HttpStream, ABC):
    primary_key = None
    state_checkpoint_interval = 1

    url_base = "https://dcm-nhn.dentclinicmanager.com/API/DCMConnect.asmx?WSDL"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.api_key = config.get("api_key")
        self.clinic_ids = self.get_clinic_ids()
        self.clinic_id = next(self.clinic_ids)

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {'Content-Type': 'application/soap+xml; charset=utf-8'}

    def get_clinic_ids(self) -> Iterator[str]:
        payload_clinics = f"""<?xml version="1.0" encoding="utf-8"?>
            <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
                <soap12:Body>
                    <GetClinics xmlns="http://tempuri.org/">
                        <key>{self.api_key}</key>
                    </GetClinics>
                </soap12:Body>
            </soap12:Envelope>
        """
        headers = {'Content-Type': 'application/soap+xml; charset=utf-8'}
        response = requests.post(
            f"{self.url_base}", data=payload_clinics, headers=headers)

        clinics = xmltodict.parse(response.text)[
            'soap:Envelope']['soap:Body']['GetClinicsResponse']['GetClinicsResult']['ClinicModel']
        clinic_ids = [x.get('Id') for x in clinics]
        return iter(clinic_ids)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """

        self.clinic_id = next(self.clinic_ids, None)
        if self.clinic_id is None:
            return None

        
        return {"clinic_id": self.clinic_id}

    def request_body_data(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return f'''<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <GetResources xmlns="http://tempuri.org/">
      <key>{self.api_key}</key>
      <clinicId>{self.clinic_id}</clinicId>
    </GetResources>
  </soap12:Body>
</soap12:Envelope>'''

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """

        path = ['soap:Envelope', 'soap:Body', 'GetResourcesResponse',
                'GetResourcesResult', 'ResourceModel']

        data = xmltodict.parse(response.text).copy()
        for key in path:
            data = data.get(key)
            if data is None:
                data = []
                break

        if type(data) == dict:
            data = [data]

        yield from data


# Basic full refresh stream
class DentclinicStream(HttpStream, ABC):
    primary_key = None
    state_checkpoint_interval = 1

    url_base = "https://dcm-nhn.dentclinicmanager.com/API/DCMConnect.asmx?WSDL"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.api_key = config.get("api_key")
        self.start_date = pendulum.parse(config.get("start_date"))
        self.months_forward = config.get("months_forward")
        self.stop_date = pendulum.today().add(months=config.get("months_forward"))
        self.cursor_start_date = self.start_date
        self.fetch_interval_days = config.get("fetch_interval_days")
        self.cursor_end_date = self.start_date.add(
            days=config.get("fetch_interval_days"))

        self.clinic_ids = self.get_clinic_ids()
        self.clinic_id = next(self.clinic_ids)

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {'Content-Type': 'application/soap+xml; charset=utf-8'}

    def get_clinic_ids(self) -> Iterator[str]:
        payload_clinics = f"""<?xml version="1.0" encoding="utf-8"?>
            <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
                <soap12:Body>
                    <GetClinics xmlns="http://tempuri.org/">
                        <key>{self.api_key}</key>
                    </GetClinics>
                </soap12:Body>
            </soap12:Envelope>
        """
        headers = {'Content-Type': 'application/soap+xml; charset=utf-8'}
        response = requests.post(
            f"{self.url_base}", data=payload_clinics, headers=headers)

        clinics = xmltodict.parse(response.text)[
            'soap:Envelope']['soap:Body']['GetClinicsResponse']['GetClinicsResult']['ClinicModel']
        clinic_ids = [x.get('Id') for x in clinics]
        return iter(clinic_ids)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """

        if self.cursor_end_date >= self.stop_date:
            self.clinic_id = next(self.clinic_ids, None)
            if self.clinic_id is None:
                return None

            self.cursor_start_date = self.start_date
            self.cursor_end_date = self.start_date.add(
                months=self.fetch_interval_days)
        else:
            self.cursor_start_date = self.cursor_start_date.add(
                months=self.fetch_interval_days)
            self.cursor_end_date = self.cursor_end_date.add(
                months=self.fetch_interval_days)

        return {"start_date": self.cursor_start_date, "end_date": self.cursor_end_date}

    def request_body_data(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return f"""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <GetBookings xmlns="http://tempuri.org/">
              <key>{self.api_key}</key>
              <clinicId>{self.clinic_id}</clinicId>
              <dateTimeStart>{self.cursor_start_date}</dateTimeStart>
              <dateTimeEnd>{self.cursor_end_date}</dateTimeEnd>
            </GetBookings>
          </soap12:Body>
        </soap12:Envelope>"""

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """

        path = ['soap:Envelope', 'soap:Body', 'GetBookingsResponse',
                'GetBookingsResult', 'BookingModel']
        data = xmltodict.parse(response.text).copy()
        for key in path:
            data = data.get(key)
            if data is None:
                data = []
                break

        if type(data) == dict:
            data = [data]

        yield from data


class Bookings(DentclinicStream):
    primary_key = "Id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        should return "bookings". Required.
        """
        return ""

    @property
    def http_method(self) -> str:
        return "POST"


class Resources(DentclinicVisidIdStream):
    primary_key = "Id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        should return "resources". Required.
        """
        return ""

    @property
    def http_method(self) -> str:
        return "POST"


class Clinics(DentclinicStaticStream):
    primary_key = "Id"
    static_endpoint = 'GetClinics'
    endpoint_data_path = ['soap:Envelope', 'soap:Body',
                          'GetClinicsResponse', 'GetClinicsResult', 'ClinicModel']

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        should return "clinics". Required.
        """
        return ""

    @property
    def http_method(self) -> str:
        return "POST"


class Services(DentclinicStaticStream):
    primary_key = "Id"
    static_endpoint = 'GetServices'
    endpoint_data_path = ['soap:Envelope', 'soap:Body',
                          'GetServicesResponse', 'GetServicesResult', 'ServiceModel']

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        should return "clinics". Required.
        """
        return ""

    @property
    def http_method(self) -> str:
        return "POST"


# Source
class SourceDentclinic(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [Bookings(config=config), Clinics(config=config), Services(config=config), Resources(config=config)]
