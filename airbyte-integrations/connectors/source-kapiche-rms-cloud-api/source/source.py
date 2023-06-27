"""
Best docs: https://restapidocs.rmscloud.com/#tag/reservations

*LoyaltyNo
*Postcode These two fields are found
in the guests data. If you use the GET/guests/{id} call and use
the "model type" = full, you can pull the fields from the response
body. Heres a link to that call on our documentation -
https://app.swaggerhub.com/apis-docs/RMSHospitality/RMS_REST_API/1.4.18.1#/guests/getGuestsById

*DateMade_medium *Nights I have logged a job for our developers
to try and get these fields added to our reservation search
call. The job reference for this is REST-1116. However the
POST/auditTrail/search will also have this in the response
body as "createdDate"

*TotalGrand This is referring to the total value of a reservation.
This can be pulled from the GET/reservations/{id}/actualAccount call.
It will be in the response body as "totalRate". Heres a link to that
call on our documentation -
https://app.swaggerhub.com/apis-docs/RMSHospitality/RMS_REST_API/1.4.18.1#/reservations/getReservationActualAccount
Hope this helps. Let us know if you have further questions on this.

"""


from __future__ import annotations
from collections.abc import Iterator

import logging
from datetime import datetime, timedelta
from itertools import islice
from typing import (
    Dict,
    Generator,
    Any,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
)

import requests
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

from .utils import cache, http_adapter

logger = logging.getLogger("airbyte")


class RmsCloudApiKapicheSource(Source):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Initialize only. It actually gets set in `check_connection`
        self.auth_token = None

    def check(
        self, logger: logging.Logger, config: Mapping[str, Any]
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
        self, logger: logging.Logger, config: Mapping[str, Any]
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
        logger: logging.Logger,
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
        state["last_date"] = 123

        properties = self._fetch_properties(logger)
        categories = self._fetch_categories(logger, properties)

        # TODO: add date_from here
        gen = self._fetch_nps(logger, properties, categories)

        for i, record in enumerate(gen):
            yield AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    namespace=None,
                    stream=stream_name,
                    data=record,
                    emitted_at=int(datetime.now().timestamp()) * 1000,
                ),
            )
            state["last_date"] = record["Departure Date"]

            if i % 10 == 0:
                # Emit state record every 10th record.
                yield AirbyteMessage(
                    type=Type.STATE,
                    state=AirbyteStateMessage(
                        state_type=AirbyteStateType.STREAM,
                        stream=AirbyteStreamState(
                            stream_descriptor=StreamDescriptor(name=stream_name),
                            stream_state=state,
                        ),
                    ),
                )

        yield AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(
                state_type=AirbyteStateType.STREAM,
                stream=AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name=stream_name),
                    stream_state=state,
                ),
            ),
        )

    def _get(self, url: str) -> dict:
        with http_adapter(backoff_factor=2) as session:
            response = session.get(url, headers={"authtoken": self.auth_token})
            response.raise_for_status()
            return response.json()

    def _post(self, url: str, payload: dict) -> dict | list:
        with http_adapter(backoff_factor=2) as session:
            response = session.post(
                url, json=payload, headers={"authtoken": self.auth_token}
            )
            response.raise_for_status()
            return response.json()

        # response = requests.post(
        #     url, json=payload, headers={"authtoken": self.auth_token}
        # )
        # return response.json()

    def get_auth_token(
        self,
        logger: logging.Logger,
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
        logger: logging.Logger,
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
        all_property_ids = list(properties)
        logger.info(all_property_ids)
        start_date = datetime(year=2022, month=8, day=1)
        end_date = datetime(year=2022, month=8, day=31)

        for date_from, date_to in date_ranges_generator(start_date, end=end_date):
            logger.info(
                f"Fetching for week {date_from.isoformat()} to {date_to.isoformat()}"
            )
            data = self._post(
                "https://restapi8.rmscloud.com/reports/npsResults",
                payload={
                    "propertyIds": all_property_ids,
                    "reportBy": "departDate",
                    "dateFrom": date_to_rms_string(date_from),
                    "dateTo": date_to_rms_string(date_to),
                    "npsRating": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                },
            )
            results = data["npsResults"]
            logger.info(f"Got {len(results)} for date range")

            # Collect all the reservation Ids upfront. We use this to fetch
            # all reservation upfront so that we can look up reservation
            # details during the construction of the output record later.
            reservation_ids = [
                s["reservationId"]
                for property_result in results
                for s in property_result.get("surveyDetails", [])
            ]

            # TODO: these can be fetched simultaneously
            reservation_lookup = {
                r["id"]: r for r in self._fetch_reservations(logger, reservation_ids)
            }
            reservation_account_lookup = {
                r["reservationId"]: r
                for r in self._fetch_reservation_accounts(logger, reservation_ids)
            }
            guest_lookup = {
                r["id"]: r for r in self._fetch_guests(logger, reservation_ids)
            }

            for result in results[:20]:
                # logger.info(result)
                # do_once('r', lambda: print(json.dumps(r, indent=2)))
                # Each "npsResult" will correspond to a single category
                property_id = result["propertyId"]
                surveys = result["surveyDetails"]
                for s in surveys:
                    # Within that "npsResult" there are many survey
                    # responses known as "surveyDetails"
                    record = {}
                    self.update_record_from_property(
                        record,
                        properties,
                        property_id,
                    )

                    category_id = s["categoryId"]
                    self.update_record_from_category(
                        record,
                        categories,
                        category_id,
                    )

                    self.update_record_from_survey_detail(record, s)

                    reservation_id = s.get("reservationId")
                    if reservation_id:
                        reservation = reservation_lookup.get(reservation_id)
                        reservation_account = reservation_account_lookup.get(
                            reservation_id, {}
                        )
                        if reservation:
                            self.update_record_from_reservation(
                                record,
                                reservation,
                                reservation_account,
                            )

                            guest = guest_lookup.get(reservation["guestId"])
                            if guest:
                                logger.info(f"{guest=}")
                                self.update_record_from_guest(record, guest)
                            else:
                                logger.warning(
                                    f"{reservation_id=} with guest "
                                    f"{reservation['guestId']=} could not "
                                    f"be found in the guest lookup map."
                                )
                        else:
                            logger.warning(
                                f"{reservation_id=} not found in the lookup table. "
                                f"Something might be wrong with how registrations are "
                                f" being prefetched."
                            )

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

                    yield record

    def reservation_data_by_id(
        self, logger: logging.Logger, reservation_ids: list[int]
    ):
        items = self._fetch_reservations(logger, reservation_ids)
        return {r["id"] for r in items}

    def update_record_from_property(
        self,
        record: dict[str, Any],
        properties: dict[int, dict[str, Any]],
        property_id: int,
    ) -> None:
        record.update(
            {
                "Property ID": property_id,
            }
        )
        prop = properties.get(property_id)
        if prop:
            record.update(
                {
                    "Property ID": prop["id"],
                    "Park Name": prop.get("name"),
                }
            )

    def update_record_from_category(
        self,
        record: dict[str, Any],
        categories: dict[int, dict[str, Any]],
        category_id: int,
    ) -> None:
        cat = categories.get(category_id)
        if cat:
            record.update(
                {
                    "Category Class": cat.get("categoryClass"),
                    "Number of Areas": cat.get("numberOfAreas"),
                    "Max Occupants Per Category": cat.get("maxOccupantsPerCategory"),
                    "Category": cat.get("name"),
                }
            )

    def update_record_from_reservation(
        self,
        record: dict[str, Any],
        reservation: dict[str, Any],
        reservation_account: dict[str, Any],
    ) -> None:
        record.update(
            {
                "Adults": reservation.get("adults"),
                "Children": reservation.get("children"),
                "Infants": reservation.get("infants"),
                "Booking Source": reservation.get("bookingSourceName"),
                "totalRate": reservation_account.get("totalRate"),
            }
        )

    def update_record_from_guest(
        self,
        record: dict[str, Any],
        guest: dict[str, Any],
    ) -> None:
        record.update(
            {
                "postcode": guest.get("postcode"),
                "loyaltyNo": bool(guest.get("loyaltyNo", "")),
                "loyaltyMembershipType": guest.get("loyaltyMembershipType", ""),
            }
        )

    def update_record_from_survey_detail(
        self,
        record: dict[str, Any],
        survey_details: dict[str, Any],
    ) -> None:
        s = survey_details
        record.update(
            {
                "Reservation ID": s["reservationId"],
                "Comments": s["comments"],
                "Arrival Date": s["arrive"],
                "Departure Date": s["depart"],
            }
        )
        # Score (NPS, Service, Facility, Site, Value)
        for name, value in s["score"].items():
            record[f"{name.title()} Rating"] = value

    # @cache("_fetch_reservations")
    def _fetch_reservations(
        self,
        logger: logging.Logger,
        reservation_ids: list[int],
        chunk_size_must_be_500_or_less: int = 100,
    ) -> list[dict[str, Any]]:
        results = []
        limit = chunk_size_must_be_500_or_less
        if limit > 500:
            raise ValueError(f"The RMS API requires {limit=} to be" "500 or less.")

        it = iter(reservation_ids)
        while chunk := list(islice(it, limit)):
            logger.debug(f"Fetching reservations chunk {len(chunk)=}")
            response = self._post(
                f"https://restapi8.rmscloud.com/reservations/search?modelType=basic&limit={limit}",
                dict(reservationIds=chunk),
            )
            results.extend(response)

        logger.debug("All reservation chunks complete.")
        return results

    def _fetch_reservation_accounts(
        self,
        logger: logging.Logger,
        reservation_ids: list[int],
    ) -> list[dict[str, Any]]:
        results = []
        limit = 50
        it = iter(reservation_ids)
        while chunk := list(islice(it, limit)):
            logger.debug(f"Fetching reservations chunk {len(chunk)=}")
            response = self._post(
                "https://restapi8.rmscloud.com/reservations/actualAccount/search",
                dict(ids=chunk),
            )
            results.extend(response)

        logger.debug("All reservation chunks complete.")
        return results

    def _fetch_guests(
        self,
        logger: logging.Logger,
        reservation_ids: list[int],
        chunk_size_must_be_500_or_less: int = 100,
    ) -> list[dict[str, Any]]:
        """
        https://restapidocs.rmscloud.com/#tag/guests/operation/postGuestSearch
        """
        results = []
        limit = chunk_size_must_be_500_or_less
        if limit > 500:
            raise ValueError(f"The RMS API requires {limit=} to be" "500 or less.")

        it = iter(reservation_ids)
        while chunk := list(islice(it, limit)):
            logger.debug(f"Fetching guests chunk {len(chunk)=}")
            response = self._post(
                f"https://restapi8.rmscloud.com/guests/search?limit={limit}&modelType=full",
                dict(reservationIds=chunk),
            )
            results.extend(response)

        logger.debug("All reservation chunks complete.")
        return results

    @cache("_fetch_properties")
    def _fetch_properties(self, logger: logging.Logger) -> dict[int, dict]:
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
        self, logger: logging.Logger, properties: dict[int, dict]
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


def date_to_rms_string(dt: datetime) -> str:
    """See "Guidelines and Formatting at:
    https://app.swaggerhub.com/apis/RMSHospitality/RMS_REST_API/1.4.18.1#/info
    """
    return datetime.strftime(dt, "%Y-%m-%d %H:%M:%S")


def date_ranges_generator(
    start_date: datetime,
    end: Optional[datetime] = None,
    span: Optional[dict[str, int]] = None,
) -> Generator[tuple[datetime, datetime], None, None]:
    """Generate a sequence of (from, to) dates."""
    if span is None:
        span = {"days": 7}

    if end:
        endf = lambda: end
    else:
        endf = lambda: datetime.now()

    if any(v < 0 for v in span.values()):
        raise ValueError("Only positive span values are allowed")

    if start_date >= endf():
        return

    dt = timedelta(**span)

    date0 = start_date
    date1 = start_date + dt
    while date0 < endf():
        yield date0, date1
        date0 = date1
        date1 = date1 + dt
