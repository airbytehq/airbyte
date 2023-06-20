from __future__ import annotations
import os
from abc import ABC, abstractmethod
from pathlib import Path
import json
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.streams.core import Stream, StreamData


class RMSCloudAPIStream(IncrementalMixin, Stream):
    # Save the state every 100 records
    # This means we're using interval based checkpointing:
    # https://docs.airbyte.com/connector-development/cdk-python/incremental-stream/#interval-based-checkpointing
    state_checkpoint_interval = 100

    def __init__(self) -> None:
        super().__init__()
        # Just for initialization. The value will be
        # managed through the state getter and setter
        # property.
        self._cursor_value = ""
        self.auth_token = ""

    @property
    def cursor_field(self) -> str:
        """This is very tricky. The API allows you to
        specify a `fromDate` and `endDate` with type "surveyDate"
        but it does not return the surveyDate anywhere in the
        responses. This makes it diffucult to use as a cursor
        field.
        """
        return "from_survey_date"

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: str(self._cursor_value)}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def get_json_schema(self) -> Mapping[str, Any]:
        # TODO: override to set schema here instead of JSON
        schema = super().get_json_schema()
        return schema

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        properties = self._fetch_properties()
        categories = self._fetch_categories(properties)
        results = self._fetch_nps(properties, categories)
        yield from results

    def _post(self, url: str, payload: dict) -> dict:
        response = requests.post(
            url,
            json=payload,
            headers={'authtoken': self.auth_token}
        )
        return response.json()

    def _fetch_nps(self, properties, categories) -> Iterable[dict[str, Any]]:
        """
        Fetch the responses on a per-property basis
        The API actually supports providing a list of properties,
        however it seems to have some undocumented limits on the
        number of survey responses it will return. I could only
        manage to get slightly over 5K responses back, after which
        it would truncate the results for most of the properties.

        So to work around this I am fetching the results for each property.
        However, a better approach might be to use a date-based partitioning
        when loading historical data. E.g. fetch across all properties, but
        on a month-by-month basis.

        https://app.swaggerhub.com/apis-docs/RMSHospitality/RMS_REST_API/1.4.16.1#/reports/npsResultsReport

        """
        for prop in properties:
            self.logger.info(f"fetching data for {prop['name']}")
            data = self._post(
                "https://restapi8.rmscloud.com/reports/npsResults",
                payload={
                    "propertyIds": [prop['id']],
                    "reportBy": "surveyDate",
                    "dateFrom": "2022-01-01 00:00:00",
                    "dateTo": "2023-06-15 00:00:00",
                    "npsRating": [
                        0,
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                        9,
                        10
                    ]
                },
            )
            results = data['npsResults']
            for r in results:
                #do_once('r', lambda: print(json.dumps(r, indent=2)))
                # Each "npsResult" will correspond to a single category
                surveys = r['surveyDetails']
                for s in surveys:
                    # Within that "npsResult" there are many survey
                    # responses known as "surveyDetails"
                    cat = categories[s['categoryId']]
                    r = {
                        'Property ID': prop['id'],
                        'Park Name': prop['name'],
                        'Reservation ID': s['reservationId'],
                        'Comments': s['comments'],
                        'Arrival Date': s['arrive'],
                        'Departure Date': s['depart'],
                        'Category Class': cat['categoryClass'],
                        'Number of Areas': cat['numberOfAreas'],
                        'Max Occupants Per Category': cat['maxOccupantsPerCategory'],
                        'Category': cat['name']


                    }
                    # Score (NPS, Service, Facility, Site, Value)
                    for name, value in s['score'].items():
                        r[f'{name.title()} Rating'] = value

                    # Fetch the specific reservation associated with the
                    # survey response.
                    # https://app.swaggerhub.com/apis-docs/RMSHospitality/RMS_REST_API/1.4.16.1#/reservations/getReservationById
                    # This takes forever obviously since we need to generate
                    # a new request for every single survey response.
                    """
                    reservation_id = s['reservationId']
                    response = requests.get(
                        f"https://restapi8.rmscloud.com/reservations/{reservation_id}?modelType=basic",
                        headers={'authtoken': auth_token}
                    )
                    res = response.json()
                    r['Adults'] = res['adults']
                    r['Children'] = res['children']
                    r['Infants'] = res['infants']
                    r['Booking Source'] = res['bookingSourceName']
                    """

                    yield r

    def _fetch_properties(self) -> dict[int, dict]:
        # Fetch a list of properties, which will be used to retrieve
        # NPS survey responses. A property represents a physical
        # location (holiday park)
        #
        # https://app.swaggerhub.com/apis-docs/RMSHospitality/RMS_REST_API/1.4.16.1#/properties/getProperties
        self.logger.info("Fetching properties")
        response = requests.get(
            "https://restapi8.rmscloud.com/properties?modelType=basic",
            headers={"authtoken": self.auth_token},
        )
        properties = response.json()
        self.logger.info(f"{len(properties)} retrieved")
        return {p["id"]: p for p in properties}

    def _fetch_categories(
            self,
            properties: dict[int, dict]
    ) -> dict[int, dict]:
        """
        Fetch a list of categories, which provide metadata for
        NPS survey responses. A category represents an accomodation
        option within a property, e.g. 'ABC-Deluxe Cabin - Sleeps 5'

        https://app.swaggerhub.com/apis-docs/RMSHospitality/RMS_REST_API/1.4.16.1#/categories/getCategories

        Example category:

        .. code-block:: json

            {
              "allowBookingByCategory": false,
              "availableToIbe": true,
              "categoryClass": "Accommodation",
              "categoryTypeGroupingId": 12,
              "glCodeId": 23,
              "inactive": false,
              "interconnecting": false,
              "longDescription": "This is a great place to stay.",
              "numberOfAreas": 3,
              "maxOccupantsPerCategory": 4,
              "maxOccupantsPerCategoryType": 0,
              "defaultArrivalTime": "15:00:00",
              "defaultDepartureTime": "10:00:00",
              "id": 8,
              "name": "Luxury Resort 123",
              "propertyId": 2
            }

        """
        property_ids = []
        categories = {}
        for prop_id, prop in properties.items():
            property_ids.append(prop_id)

            self.logger.info(f"Fetching categories for property {prop['name']} ({prop['id']})")
            response = requests.get(
                f"https://restapi8.rmscloud.com/categories?modelType=basic&propertyId={prop['id']}",
                headers={"authtoken": self.auth_token},
            )
            property_categories = response.json()
            self.logger.info(f"{len(property_categories)} retrieved")
            for c in property_categories:
                categories[c["id"]] = c

        return categories


# Source
class Source(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        """
        Connection check to validate that the config can be used
        to connect to the Export API.

        :param config:  the user-input config object conforming
            to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input
            config can be used to connect to the API
            successfully, (False, error) otherwise.
        """
        auth_body = {
            "agentId": config['agent_id'],
            "agentPassword": config["agent_password"],
            "clientId": config['client_id'],
            "clientPassword": config["client_password"],
            "moduleType": ["guestServices"],
        }

        logger.info("Generating auth token")
        response = requests.post(
            "https://restapi8.rmscloud.com/authToken", json=auth_body
        )

        if response.status_code != 200:
            return False, Exception(response.content)

        auth_token = response.json()["token"]
        self.auth_token = auth_token
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Calls the 'list' endpoint to return streams for all active
        analysis exports for the site configured.

        :param config: A Mapping of the user input configuration
            as defined in the connector spec.
        """
        # TODO: still needs to be updated

        # Call the list endpoint and get all the exports available
        auth = TokenAuthenticator(token=config["api_token"], auth_method="Site")
        export_list_stream = ExportDataList(
            authenticator=auth, url=config["export_api_url"]
        )

        request = export_list_stream._create_prepared_request(
            path="export/list/",
            headers={"Site-Name": config["site_name"], **auth.get_auth_header()},
        )
        response = export_list_stream._send_request(request, {})

        if response.status_code != 200:
            raise Exception("List endpoint request failed!!")

        data = response.json()
        export_list = [
            ExportDataGet(
                export["uuid"],
                auth,
                export["export_url"],
                f"{export['project_name']}-{export['analysis_name']}",
                config["site_name"],
                config["vertical_themes"],
                config["theme_level_separator"],
            )
            for export in data
            if export.get("enabled")
        ]

        return export_list
