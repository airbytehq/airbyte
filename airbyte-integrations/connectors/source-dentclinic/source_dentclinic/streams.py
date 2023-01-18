from __future__ import annotations
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Iterator
import requests
import pendulum
import xmltodict
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class DentclinicBookingStream(HttpStream, ABC):
    primary_key = None
    state_checkpoint_interval = 1

    url_base = "https://dcm-nhn.dentclinicmanager.com/API/DCMConnect.asmx?WSDL"

    def __init__(self, config: Mapping[str, Any], enable_days_back_limit: bool = False, **kwargs):
        super().__init__()
        self.fetch_interval_days = int(config.get('fetch_interval_days', 1))

        self.api_key = config.get("api_key")
        self.days_forward = int(config.get("days_forward"))

        self.start_date = pendulum.parse(config.get("start_date"))
        if enable_days_back_limit:
            self.start_date = max(self.start_date, pendulum.today().add(days = -int(config.get('days_back'))))
        self.stop_date = pendulum.today().add(days=self.days_forward)

        self.cursor_start_date = self.start_date
        self.cursor_end_date = self.start_date.add(days=self.fetch_interval_days)

        self.clinic_ids = self.get_clinic_ids()
        self.clinic_id = next(self.clinic_ids)

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {'Content-Type': 'application/soap+xml; charset=utf-8'}

    @property
    def cursor_field(self) -> str:
        """
        :return str: The name of the cursor field.
        """
        return "stop_date"

    @property
    def raise_on_http_errors(self) -> bool:
        """
        Override if needed. If set to False, allows opting-out of raising HTTP code exception.
        """
        return False

    def should_retry(self, response: requests.Response) -> bool:
        """
        Override to set different conditions for backoff based on the response from the server.

        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors

        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
        """
        return response.status_code == 429 or 501 <= response.status_code < 600

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
        response = requests.post(f"{self.url_base}", data=payload_clinics, headers=headers)

        clinics = xmltodict.parse(response.text)['soap:Envelope']['soap:Body']['GetClinicsResponse']['GetClinicsResult']['ClinicModel']
        clinic_ids = [x.get('Id') for x in clinics]
        return iter(clinic_ids)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """

        print("*" * 100)
        print({"clinic_id": self.clinic_id, "start_date": self.cursor_start_date, "end_date": self.cursor_end_date})
        print("*" * 100)

        if self.clinic_id is None:
            return None

        return {"start_date": self.cursor_start_date, "end_date": self.cursor_end_date}

    def request_body_data(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
                          next_page_token: Mapping[str, Any] = None, ) -> Optional[Mapping]:

        if self.cursor_end_date >= self.stop_date:
            self.clinic_id = next(self.clinic_ids, None)
            if self.clinic_id is None:
                return ""

            self.cursor_start_date = self.start_date
            self.cursor_end_date = self.start_date.add(days=self.fetch_interval_days)
        else:
            self.cursor_start_date = self.cursor_start_date.add(days=self.fetch_interval_days)
            self.cursor_end_date = self.cursor_end_date.add(days=self.fetch_interval_days)

        start_ts = self.cursor_start_date
        end_ts = self.cursor_end_date

        clinic_state = stream_state.get(self.cursor_field, {}).get(self.clinic_id)
        if clinic_state:
            state_ts = pendulum.parse(clinic_state)
            start_ts = max(start_ts, state_ts)
            end_ts = start_ts.add(days=self.fetch_interval_days)

        return f"""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <GetBookings xmlns="http://tempuri.org/">
              <key>{self.api_key}</key>
              <clinicId>{self.clinic_id}</clinicId>
              <dateTimeStart>{start_ts}</dateTimeStart>
              <dateTimeEnd>{end_ts}</dateTimeEnd>
            </GetBookings>
          </soap12:Body>
        </soap12:Envelope>"""

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """

        path = ['soap:Envelope', 'soap:Body', 'GetBookingsResponse', 'GetBookingsResult', 'BookingModel']
        data = xmltodict.parse(response.text).copy()
        for key in path:
            data = data.get(key)
            if data is None:
                data = []
                break

        if type(data) == dict:
            data = [data]

        yield from data



class DentclinicUtilizationStream(HttpStream, ABC):
    primary_key = None
    state_checkpoint_interval = 1

    url_base = "https://dcm-nhn.dentclinicmanager.com/API/DCMConnect.asmx?WSDL"

    def __init__(self, config: Mapping[str, Any], enable_days_back_limit: bool = False, **kwargs):
        super().__init__()
        self.fetch_interval_days = int(config.get('fetch_interval_days', 1))

        self.api_key = config.get("api_key")
        self.days_forward = int(config.get("days_forward"))

        self.start_date = pendulum.parse(config.get("start_date"))
        if enable_days_back_limit:
            self.start_date = max(self.start_date, pendulum.today().add(days = -int(config.get('days_back'))))
        self.stop_date = pendulum.today().add(days=self.days_forward)

        self.cursor_start_date = self.start_date
        self.cursor_end_date = self.start_date.add(days=self.fetch_interval_days)

        self.clinic_ids = self.get_clinic_ids()
        self.clinic_id = next(self.clinic_ids)

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {'Content-Type': 'application/soap+xml; charset=utf-8'}

    @property
    def cursor_field(self) -> str:
        """
        :return str: The name of the cursor field.
        """
        return "stop_date"

    @property
    def raise_on_http_errors(self) -> bool:
        """
        Override if needed. If set to False, allows opting-out of raising HTTP code exception.
        """
        return False

    def should_retry(self, response: requests.Response) -> bool:
        """
        Override to set different conditions for backoff based on the response from the server.

        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors

        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
        """
        return response.status_code == 429 or 501 <= response.status_code < 600

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
        response = requests.post(f"{self.url_base}", data=payload_clinics, headers=headers)

        clinics = xmltodict.parse(response.text)['soap:Envelope']['soap:Body']['GetClinicsResponse']['GetClinicsResult']['ClinicModel']
        clinic_ids = [x.get('Id') for x in clinics]
        return iter(clinic_ids)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """

        print("*" * 100)
        print({"clinic_id": self.clinic_id, "start_date": self.cursor_start_date, "end_date": self.cursor_end_date})
        print("*" * 100)

        if self.clinic_id is None:
            return None

        return {"start_date": self.cursor_start_date, "end_date": self.cursor_end_date}

    def request_body_data(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
                          next_page_token: Mapping[str, Any] = None, ) -> Optional[Mapping]:

        if self.cursor_end_date >= self.stop_date:
            self.clinic_id = next(self.clinic_ids, None)
            if self.clinic_id is None:
                return ""

            self.cursor_start_date = self.start_date
            self.cursor_end_date = self.start_date.add(days=self.fetch_interval_days)
        else:
            self.cursor_start_date = self.cursor_start_date.add(days=self.fetch_interval_days)
            self.cursor_end_date = self.cursor_end_date.add(days=self.fetch_interval_days)

        start_ts = self.cursor_start_date
        end_ts = self.cursor_end_date

        clinic_state = stream_state.get(self.cursor_field, {}).get(self.clinic_id)
        if clinic_state:
            state_ts = pendulum.parse(clinic_state)
            start_ts = max(start_ts, state_ts)
            end_ts = start_ts.add(days=self.fetch_interval_days)

        return f"""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <GetUtilizationReport xmlns="http://tempuri.org/">
              <key>{self.api_key}</key>
              <clinicId>{self.clinic_id}</clinicId>
              <dateFrom>{start_ts}</dateFrom>
              <dateUntil>{end_ts}</dateUntil>
            </GetUtilizationReport>
          </soap12:Body>
        </soap12:Envelope>"""

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """

        path = ['soap:Envelope', 'soap:Body', 'GetUtilizationReportResponse', 'GetUtilizationReportResult','ProfessionalsAndShifts','ProfessionalShifts']
        data = xmltodict.parse(response.text).copy()
        for key in path:
            data = data.get(key)
            if data is None:
                data = []
                break

        if type(data) == dict:
            data = [data]

        yield from data


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


class DentclinicClinicIdsStream(HttpStream, ABC):
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
        response = requests.post(f"{self.url_base}", data=payload_clinics, headers=headers)

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

        path = ['soap:Envelope', 'soap:Body', 'GetResourcesResponse', 'GetResourcesResult', 'ResourceModel']

        data = xmltodict.parse(response.text).copy()
        for key in path:
            data = data.get(key)
            if data is None:
                data = []
                break

        if type(data) == dict:
            data = [data]

        yield from data
