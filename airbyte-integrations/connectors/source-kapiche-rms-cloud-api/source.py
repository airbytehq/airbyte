from __future__ import annotations

import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, Generator

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    Status,
    StreamDescriptor,
    Type,
)
from airbyte_cdk.sources import Source


from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.streams.core import Stream, StreamData

logger = AirbyteLogger()

def cache(path: str):
    def outer(f):
        def inner(*args, **kwargs):
            cache = Path(f"cache-{path}")
            if cache.exists():
                logger.info(f"Using cache for {path}")
                pickled = cache.read_bytes()
                return pickle.loads(cache.read_bytes())
            else:
                result = f(*args, **kwargs)
                pickled = pickle.dumps(result)
                cache.write_bytes(pickled)
                return result

        return inner

    return outer


class RmsCloudApiKapicheSource(Source):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.auth_token = None

    def check(
        self, logger: AirbyteLogger, config: Mapping[str, Any]
    ) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration
            e.g: if a provided Stripe API token can be used to connect to the Stripe API.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            auth_token = self.get_auth_token(logger, config)
            self.auth_token = auth_token
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except requests.HTTPError as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED, message=f"HTTP error: {e}"
            )
        except Exception as e:
            msg = f"An unexpected error occurred: {e}"
            logger.exception(msg)
            return AirbyteConnectionStatus(status=Status.FAILED, message=msg)

    def discover(
        self, logger: AirbyteLogger, config: Mapping[str, Any]
    ) -> AirbyteCatalog:
        """
        Returns an AirbyteCatalog representing the available streams and fields in this integration.
        For example, given valid credentials to a Postgres database,
        returns an Airbyte catalog where each postgres table is a stream, and each table column is a field.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteCatalog is an object describing a list of all available streams in this source.
            A stream is an AirbyteStream object that includes:
            - its stream name (or table name in the case of Postgres)
            - json_schema providing the specifications of expected schema for this stream (a list of columns described
            by their names and types)
        """
        streams = []

        stream_name = "RMSNPS"  # Example
        json_schema = {  # Example
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "Property ID": {"type": "integer"},
                "Park Name": {"type": "string"},
                "Reservation ID": {"type": "integer"},
                "Comments": {"type": "string"},
                "Arrival Date": {"type": "string"},
                "Departure Date": {"type": "string"},
                "Category Class": {"type": "string"},
                "Number of Areas": {"type": "integer"},
                "Max Occupants Per Category": {"type": "integer"},
                "Category": {"type": "string"},
                "Nps Rating": {"type": "number"},
                "Service Rating": {"type": "number"},
                "Facility Rating": {"type": "number"},
                "Site Rating": {"type": "number"},
                "Value Rating": {"type": "number"},
                # "Adults": {"type": "integer"},
                # "Children": {"type": "integer"},
                # "Infants": {"type": "integer"},
                "Booking Source": {"type": "string"},
            },
        }

        """
        Extra:
            LoyaltyNo – currently this is a unique number but I just want it to be a yes/no. Yes if there is a number, no if there’s not. It’s to know if a guest is a loyalty member or not.
            TotalGrand – the total cost of the booking.
            Nights – the number of nights the booking was for.
            DateMade_medium – the date the booking was made
            Adults – the number of adults on the booking
            Children – the number of kids
            Infants – the number of infants
            Postcode
        """
        streams.append(
            AirbyteStream(
                name=stream_name,
                json_schema=json_schema,
                supported_sync_modes=["full_refresh", "incremental"],
                source_defined_cursor=False,
            )
        )
        return AirbyteCatalog(streams=streams)

    def read(
        self,
        logger: AirbyteLogger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Dict[str, Any],
    ) -> Generator[AirbyteMessage, None, None]:
        """
        Returns a generator of the AirbyteMessages generated by reading the source with the given configuration,
        catalog, and state.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
            the properties of the spec.yaml file
        :param catalog: The input catalog is a ConfiguredAirbyteCatalog which is almost the same as AirbyteCatalog
            returned by discover(), but
        in addition, it's been configured in the UI! For each particular stream and field, there may have been provided
        with extra modifications such as: filtering streams and/or columns out, renaming some entities, etc
        :param state: When a Airbyte reads data from a source, it might need to keep a checkpoint cursor to resume
            replication in the future from that saved checkpoint.
            This is the object that is provided with state from previous runs and avoid replicating the entire set of
            data everytime.

        :return: A generator that produces a stream of AirbyteRecordMessage contained in AirbyteMessage object.
        """
        stream_name = "RMSNPS"  # Example

        if not self.auth_token:
            # This is to handle calling read from the CLI
            # as in `python main.py read ...`. In this scenario
            # `check()` is not called.
            self.auth_token = self.get_auth_token(logger, config)

        logger.info(f"catalog: {catalog}")
        logger.info(f"state: {state}")
        state['last_date'] = 123

        properties = self._fetch_properties(logger)
        categories = self._fetch_categories(logger, properties)
        gen = self._fetch_nps(logger, properties, categories)

        from itertools import islice
        for record in islice(gen, 1):
            yield AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    namespace=None,
                    stream=stream_name,
                    data=record,
                    emitted_at=int(datetime.now().timestamp()) * 1000,
                ),
            )
            state['last_date'] = 456

            yield AirbyteMessage(
                type=Type.STATE,
                state=AirbyteStateMessage(
                    state_type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name=stream_name),
                        stream_state=state,
                    ),
                )
            )

    def _get(self, url: str, payload: dict) -> dict:
        response = requests.get(url, headers={"authtoken": self.auth_token})
        return response.json()

    def _post(self, url: str, payload: dict) -> dict:
        response = requests.post(
            url, json=payload, headers={"authtoken": self.auth_token}
        )
        return response.json()

    def get_auth_token(
        self,
        logger: AirbyteLogger,
        config: Mapping[str, Any],
    ):
        auth_body = {
            "agentId": config["agent_id"],
            "agentPassword": config["agent_password"],
            "clientId": config["client_id"],
            "clientPassword": config["client_password"],
            "moduleType": ["guestServices"],
        }

        logger.info("Generating auth token")
        # TODO: retry. Perhaps make a session object after
        # receiving the token, with retries configured on
        # the session object.
        response = requests.post(
            "https://restapi8.rmscloud.com/authToken", json=auth_body
        )
        response.raise_for_status()
        auth_token = response.json()["token"]
        return auth_token

    def _fetch_nps(
        self,
        logger: AirbyteLogger,
        properties: dict[int, dict],
        categories: dict[int, dict],
    ) -> Iterable[dict[str, Any]]:
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
        for prop_id, prop in properties.items():
            logger.info(f"fetching data for {prop['name']}")
            data = self._post(
                "https://restapi8.rmscloud.com/reports/npsResults",
                payload={
                    "propertyIds": [prop_id],
                    "reportBy": "surveyDate",
                    "dateFrom": "2022-01-01 00:00:00",
                    "dateTo": "2023-06-15 00:00:00",
                    "npsRating": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                },
            )
            results = data["npsResults"]
            for r in results:
                # do_once('r', lambda: print(json.dumps(r, indent=2)))
                # Each "npsResult" will correspond to a single category
                surveys = r["surveyDetails"]
                for s in surveys:
                    # Within that "npsResult" there are many survey
                    # responses known as "surveyDetails"
                    cat = categories[s["categoryId"]]
                    r = {
                        "Property ID": prop["id"],
                        "Park Name": prop["name"],
                        "Reservation ID": s["reservationId"],
                        "Comments": s["comments"],
                        "Arrival Date": s["arrive"],
                        "Departure Date": s["depart"],
                        "Category Class": cat["categoryClass"],
                        "Number of Areas": cat["numberOfAreas"],
                        "Max Occupants Per Category": cat["maxOccupantsPerCategory"],
                        "Category": cat["name"],
                    }
                    # Score (NPS, Service, Facility, Site, Value)
                    for name, value in s["score"].items():
                        r[f"{name.title()} Rating"] = value

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

    def reservation_data_by_id(self, logger: AirbyteLogger, reservation_ids: list[int]):
        items = self._fetch_reservations(logger, reservation_ids)
        return {r["id"] for r in items}

    # @cache("_fetch_reservations")
    def _fetch_reservations(
        self, logger: AirbyteLogger, reservation_ids: list[int]
    ) -> list[dict[str, Any]]:
        response = requests.post(
            "https://restapi8.rmscloud.com/reservations/search?modelType=basic",
            headers={"authtoken": self.auth_token},
            json=dict(reservationIds=reservation_ids),
        )
        return response.json()

    @cache("_fetch_properties")
    def _fetch_properties(self, logger: AirbyteLogger) -> dict[int, dict]:
        # Fetch a list of properties, which will be used to retrieve
        # NPS survey responses. A property represents a physical
        # location (holiday park)
        #
        # https://app.swaggerhub.com/apis-docs/RMSHospitality/RMS_REST_API/1.4.16.1#/properties/getProperties
        logger.info("Fetching properties")
        response = requests.get(
            "https://restapi8.rmscloud.com/properties?modelType=basic",
            headers={"authtoken": self.auth_token},
        )
        properties = response.json()
        logger.info(f"{len(properties)} retrieved")
        return {p["id"]: p for p in properties}

    @cache("_fetch_categories")
    def _fetch_categories(
        self, logger: AirbyteLogger, properties: dict[int, dict]
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
        categories = {}
        for prop_id, prop in properties.items():
            logger.info(f"Fetching categories for property {prop['name']} ({prop_id})")
            response = requests.get(
                f"https://restapi8.rmscloud.com/categories?modelType=basic&propertyId={prop['id']}",
                headers={"authtoken": self.auth_token},
            )
            property_categories = response.json()
            logger.info(f"{len(property_categories)} retrieved")
            for c in property_categories:
                categories[c["id"]] = c

        return categories
