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
from collections import deque
import logging
from datetime import datetime, timedelta, tzinfo, timezone
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
from zoneinfo import ZoneInfo

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
        if the input configuration can be used to successfully
        connect to the integration e.g: if a provided Stripe API
        token can be used to connect to the Stripe API.

        :param logger: Logging object to display debug/info/error to
            the logs (logs will not be accessible via airbyte UI if they
            are not passed to this logger)

        :param config: Json object containing the configuration of
            this source, content of this json is as specified in the
            properties of the spec.yaml file

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
        Returns an AirbyteCatalog representing the available streams
        and fields in this integration. For example, given valid
        credentials to a Postgres database, returns an Airbyte
        catalog where each postgres table is a stream, and each table
        column is a field.

        :param logger: Logging object to display debug/info/error to
            the logs (logs will not be accessible via airbyte UI if they
            are not passed to this logger)
        :param config: Json object containing the configuration of this source,
            content of this json is as specified in the properties of the
            spec.yaml file

        :return: AirbyteCatalog is an object describing a list of all
        available streams in this source. A stream is an
        AirbyteStream object that includes:
            - its stream name (or table name in the case of Postgres)
            - json_schema providing the specifications of expected
              schema for this stream (a list of columns described by
              their names and types)
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
                "Reservation Created Date": {
                    "type": "string",
                    "format": "date-time",
                    "airbyte_type": "timestamp_with_timezone",
                },
                "Arrival Date": {
                    "type": "string",
                    "format": "date-time",
                    "airbyte_type": "timestamp_with_timezone",
                },
                "Departure Date": {
                    "type": "string",
                    "format": "date-time",
                    "airbyte_type": "timestamp_with_timezone",
                },
                # This field is calculated from the departure date
                # and the arrival date.
                "Nights": {"type": ["integer", "null"]},
                "Category Class": {"type": "string"},
                "Number of Areas": {"type": "integer"},
                "Max Occupants Per Category": {"type": "integer"},
                "Category": {"type": "string"},
                "Nps Rating": {"type": "number"},
                "Service Rating": {"type": "number"},
                "Facility Rating": {"type": "number"},
                "Site Rating": {"type": "number"},
                "Value Rating": {"type": "number"},
                "Booking Source": {"type": ["string", "null"]},
                # Found in the reservation=full dataset
                "Adults": {"type": ["integer", "null"]},
                "Children": {"type": ["integer", "null"]},
                "Infants": {"type": ["integer", "null"]},
                # Found in the guest=full dataset
                "Loyalty Member": {"type": "boolean"},
                "Post Code": {"type": ["string", "null"]},
                # Found in the reservation-account dataset
                "Total Rate": {"type": ["number", "null"]},
                # Nights
                # DateMade_medium
            },
        }

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
        Returns a generator of the AirbyteMessages generated by
        reading the source with the given configuration, catalog, and
        state.

        :param logger: Logging object to display debug/info/error to
            the logs (logs will not be accessible via airbyte UI if they
            are not passed to this logger)

        :param config: Json object containing the configuration of
            this source, content of this json is as specified in the
            properties of the spec.yaml file

        :param catalog: The input catalog is a
            ConfiguredAirbyteCatalog which is almost the same as
            AirbyteCatalog returned by discover(), but in addition, it's
            been configured in the UI! For each particular stream and
            field, there may have been provided with extra modifications
            such as: filtering streams and/or columns out, renaming some
            entities, etc

        :param state: When a Airbyte reads data from a source, it
            might need to keep a checkpoint cursor to resume replication
            in the future from that saved checkpoint. This is the object
            that is provided with state from previous runs and avoid
            replicating the entire set of data everytime.

        :return: A generator that produces a stream of
            AirbyteRecordMessage contained in AirbyteMessage object.
        """
        stream_name = "RMSNPS"  # Example
        state_key = "start_date"
        state_previous_reservations_key = "reservation_ids"

        if not self.auth_token:
            # This is to handle calling read from the CLI
            # as in `python main.py read ...`. In this scenario
            # `check()` is not called.
            self.auth_token = self.get_auth_token(logger, config)

        logger.info(f"catalog: {catalog}")
        logger.info(f"{list(state.keys())=}")

        # Obtain the start date from the state
        if start_date_str := state.get(state_key):
            logger.info(f"Got previous state: {start_date_str=}")
            start_date = datetime.fromisoformat(start_date_str)
        else:
            # Fallback: start from the beginning as defined in the config
            if start_date_str := config.get(state_key):
                logger.info(f"Fall back to get config start date: {start_date_str=}")
                start_date = datetime.fromisoformat(start_date_str)
                if not start_date.tzinfo:
                    start_date = start_date.replace(tzinfo=timezone.utc)
            else:
                logger.info("Fall way back to setting start date to a year ago.")
                start_date = datetime.now(timezone.utc) - timedelta(weeks=52)

        # For safety, we're going to start search for a start date that
        # is older that our actual "start date" marker. We aren't sure
        # that the `departDate` field is going to be monotonically
        # increasing with insertion in the RMS system. So we'll wind
        # back the start date a little, hoping to catch any new
        # records that might have older start dates than our current
        # start date. To avoid emitting duplicates, we're tracking
        # previously-emitted records with the `reservation-*` variables
        # which are persisted through the `state` mechanism.
        gen = self._fetch_nps(logger, start_date - timedelta(days=7))
        record = None

        # A deque for recency truncation.
        if state_previous_reservations_key not in state:
            state[state_previous_reservations_key] = deque(maxlen=10000)
        else:
            # The `state` blob store doesn't retain the deque type
            # so we have to reconstruct it from the list they
            # give back to us.
            state[state_previous_reservations_key] = deque(
                state[state_previous_reservations_key],
                maxlen=10000
            )
            logger.info(
                f"Type of the previous reservations fetched: {type(state[state_previous_reservations_key])}"
            )

        reservation_ids_already_fetched_set = set(
            state[state_previous_reservations_key]
        )
        at_least_one_new_record = False

        for i, record in enumerate(gen):
            # Manage the cache of previously-fetched reservations.
            reservation_id = record["Reservation ID"]

            if reservation_id in reservation_ids_already_fetched_set:
                logger.info(
                    f"Received {reservation_id=} but this has already been found. "
                    "Discarding."
                )
                continue

            at_least_one_new_record = True

            state[state_previous_reservations_key].append(reservation_id)
            reservation_ids_already_fetched_set.add(reservation_id)

            yield AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    stream=stream_name,
                    data=record,
                    emitted_at=int(datetime.utcnow().timestamp()) * 1000,
                ),
            )

            # TODO: would be nicer to save the most recent departure date value,
            #  but it gets complicated to implement with out state events are
            #  emitted.
            # if state[state_key]:
            #     existing_marker = datetime.fromisoformat(state[state_key])
            #     new_marker = datetime.fromisoformat(record["Departure Date"])
            #     if new_marker > existing_marker:
                    # Only update the marker if the received data is later.

            state[state_key] = record["Departure Date"]

            if i % 10 == 0:
                # Emit state record every 10th record.
                # This is the v2 state message structure below
                # yield AirbyteMessage(
                #     type=Type.STATE,
                #     state=AirbyteStateMessage(
                #         state_type=AirbyteStateType.STREAM,
                #         stream=AirbyteStreamState(
                #             stream_descriptor=StreamDescriptor(name=stream_name),
                #             stream_state=state,
                #         ),
                #     ),
                # )

                yield AirbyteMessage(
                    type=Type.STATE,
                    state=AirbyteStateMessage(
                        data=state,
                    ),
                )

        # This is the v2 state message structure below
        # yield AirbyteMessage(
        #     type=Type.STATE,
        #     state=AirbyteStateMessage(
        #         state_type=AirbyteStateType.STREAM,
        #         stream=AirbyteStreamState(
        #             stream_descriptor=StreamDescriptor(name=stream_name),
        #             stream_state=state,
        #         ),
        #     ),
        # )

        if at_least_one_new_record:
            yield AirbyteMessage(
                type=Type.STATE,
                state=AirbyteStateMessage(
                    data=state,
                ),
            )

            if record:
                logger.info(f"Final record: {record}")
            logger.info(f"Final state: {state}")

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
        start_date: datetime,
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
        properties = self._fetch_properties(logger)
        # `categories` will be overwritten with real data as
        # soon as we know there is work to do. This is an
        # optimization to make a sync faster in the case there
        # is no new data.
        categories = None

        all_property_ids = list(properties)
        # Add one to correct for the minus-one subtraction on `date_to`
        # in the loop below. See the comment there for more details.
        end_date = datetime.now(start_date.tzinfo) + timedelta(days=1)

        for date_from, date_to in date_ranges_generator(start_date, end=end_date):
            # The `npsResults` endpoint, using `departDate` as the filter,
            # matches only against WHOLE DAYS. To avoid getting duplicate
            # records back from the end of one date range, and the start of
            # the next, we have to decrement the end search date by one day.
            date_to = date_to - timedelta(days=1)
            logger.info(
                f"Fetching for week {date_from.isoformat()} to {date_to.isoformat()}"
            )
            for properties_chunk in chunks(all_property_ids, 5):
                payload = {
                    "propertyIds": properties_chunk,
                    "reportBy": "departDate",
                    "dateFrom": date_to_rms_string(date_from),
                    "dateTo": date_to_rms_string(date_to),
                    "npsRating": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                }
                logger.debug(f"{payload=}")
                data = self._post(
                    "https://restapi8.rmscloud.com/reports/npsResults",
                    payload=payload,
                )
                results = data["npsResults"]
                logger.info(f"Got {len(results)} npsResults for date range")
                if not results:
                    continue

                if not categories:
                    # `categories` has not yet been loaded, fetch now and
                    # store for use during the rest of the sync.
                    categories = self._fetch_categories(logger, properties)

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

                for result in results:
                    # Each "npsResult" will correspond to a single category
                    property_id = result["propertyId"]
                    logger.info(f"{property_id=}")
                    property = properties[property_id]
                    surveys = result["surveyDetails"]
                    logger.info(f"{len(surveys)=}")
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

                        self.update_record_from_survey_detail(
                            record, s, rms_timezone_name=property["timeZone"]
                        )

                        reservation_id = s.get("reservationId")
                        logger.info(f"{reservation_id=}")
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
                                    rms_timezone_name=property["timeZone"],
                                )

                                guest = guest_lookup.get(reservation["guestId"])
                                if guest:
                                    logger.debug(f"{guest=}")
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
        rms_timezone_name: str,
    ) -> None:
        created = convert_rms_datetime_to_python_datetime(
            rms_datetime=reservation["createdDate"],
            rms_property_timezone_windows_id_name=rms_timezone_name,
        )
        record.update(
            {
                "Adults": reservation.get("adults"),
                "Children": reservation.get("children"),
                "Infants": reservation.get("infants"),
                "Booking Source": reservation.get("bookingSourceName"),
                "Total Rate": reservation_account.get("totalRate"),
                "Reservation Created Date": created.isoformat(),
            }
        )

    def update_record_from_guest(
        self,
        record: dict[str, Any],
        guest: dict[str, Any],
    ) -> None:
        record.update(
            {
                "Post Code": guest.get("postCode"),
                "Loyalty Member": bool(guest.get("loyaltyNumber", "")),
            }
        )

    def update_record_from_survey_detail(
        self,
        record: dict[str, Any],
        survey_details: dict[str, Any],
        rms_timezone_name: str,
    ) -> None:
        s = survey_details
        arrival_date = convert_rms_datetime_to_python_datetime(
            rms_datetime=s["arrive"],
            rms_property_timezone_windows_id_name=rms_timezone_name,
        )
        departure_date = convert_rms_datetime_to_python_datetime(
            rms_datetime=s["depart"],
            rms_property_timezone_windows_id_name=rms_timezone_name,
        )
        # Important to strip the time component below, otherwise
        # you get incorrect deltas of days.
        nights = (departure_date.date() - arrival_date.date()).days
        record.update(
            {
                "Reservation ID": s["reservationId"],
                "Comments": s["comments"],
                "Arrival Date": arrival_date.isoformat(),
                "Departure Date": departure_date.isoformat(),
                "Nights": nights,
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
            # NOTE: `modelType=full` is required to get `createdDate`
            response = self._post(
                f"https://restapi8.rmscloud.com/reservations/search?modelType=full&limit={limit}",
                dict(reservationIds=chunk),
            )
            results.extend(response)

        missing_reservations = set(reservation_ids) - set(r["id"] for r in results)
        if missing_reservations:
            logger.warning(
                f"These reservation IDs were present in survey results but could "
                f"not be found in the reservations table: {missing_reservations}. "
                "The survey data will still be captured but expanded metadata will "
                "be missing."
            )

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

    # @cache("_fetch_properties")
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
        logger.info(f"{len(properties)} properties retrieved")
        return {p["id"]: p for p in properties}

    # @cache("_fetch_categories")
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
        logger.info("Fetching categories...")
        categories = {}
        for prop_id, prop in properties.items():
            logger.debug(f"Fetching categories for property {prop['name']} ({prop_id})")
            response = requests.get(
                f"https://restapi8.rmscloud.com/categories?modelType=basic&propertyId={prop['id']}",
                headers={"authtoken": self.auth_token},
            )
            property_categories = response.json()
            logger.debug(f"{len(property_categories)} retrieved")
            for c in property_categories:
                categories[c["id"]] = c

        logger.info("Categories fetched.")
        return categories


def date_to_rms_string(dt: datetime, as_utc=False) -> str:
    """See "Guidelines and Formatting at:
    https://app.swaggerhub.com/apis/RMSHospitality/RMS_REST_API/1.4.18.1#/info
    """
    if as_utc:
        dt = dt.astimezone(timezone.utc)

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
        # Because we compare our rolling date to the
        # end date, it's important that either they're both
        # naive or both aware. The following will work
        # for both cases, because `datetime.now(None)`
        # is valid and returns a naive datetime.
        endf = lambda: datetime.now(start_date.tzinfo)

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


def convert_rms_datetime_to_python_datetime(
    rms_datetime: str,
    rms_property_timezone_windows_id_name: str,
) -> datetime:
    """Here is an example of what this function achieves:

    .. code-block:: python

        >>> datetime.now().replace(
        ...    tzinfo=zoneinfo.ZoneInfo("Australia/Sydney")
        ... ).isoformat()
        '2023-06-29T12:09:18.975003+10:00'

    There is an extra step though: we first convert the
    Windows ID name, e.g. "AUS Eastern Standard Time"
    to the Python-compatible "Australa/Sydney" name.

    :raises ValueError: if the given Windows timezone cannot
        be found in the local lookup table.
    """
    # This does work, e.g.
    # >>> d = datetime.fromisoformat("2023-06-21 23:52:00")
    # >>> d.ctime()
    # 'Wed Jun 21 23:52:00 2023'
    # You don't need the "T"
    dt = datetime.fromisoformat(rms_datetime)
    # Attempt to convert the RMS timezone name into
    # a Python-compatible datetime object.
    if tzname := rms_timezone_to_python_timezone(rms_property_timezone_windows_id_name):
        import zoneinfo

        tzinfo = zoneinfo.ZoneInfo(tzname)
        return dt.replace(tzinfo=tzinfo)
    else:
        raise ValueError(
            f"Failed to recognize RMS timezone str "
            f"{rms_property_timezone_windows_id_name} "
            "as a known timezone value"
        )


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def rms_timezone_to_python_timezone(s: str) -> str | None:
    """RMS Properties appear to use Windows timezone IDs to
    specify timezones in properties. It's a bit of work to get these
    into python-compatible structures. Here is a stackoverflow post
    where someone generated the following lookup table that can be
    used.
    https://stackoverflow.com/a/16157049

    Here is an example of a property object with the timezone
    specified:

    .. code-block:: json

        {
          "accountingDate": "2023-06-21 00:00:00",
          "code": "xxx",
          "clientId": xxx,
          "timeZone": "AUS Eastern Standard Time",
          "useSecondaryCurrency": "false",
          "id": xxx,
          "name": "xxx",
          "inactive": false
        },

    """
    lookup = {
        "AUS Central Standard Time": "Australia/Darwin",
        "AUS Eastern Standard Time": "Australia/Sydney",
        "Afghanistan Standard Time": "Asia/Kabul",
        "Alaskan Standard Time": "America/Anchorage",
        "Arab Standard Time": "Asia/Riyadh",
        "Arabian Standard Time": "Asia/Dubai",
        "Arabic Standard Time": "Asia/Baghdad",
        "Argentina Standard Time": "America/Buenos_Aires",
        "Atlantic Standard Time": "America/Halifax",
        "Azerbaijan Standard Time": "Asia/Baku",
        "Azores Standard Time": "Atlantic/Azores",
        "Bahia Standard Time": "America/Bahia",
        "Bangladesh Standard Time": "Asia/Dhaka",
        "Canada Central Standard Time": "America/Regina",
        "Cape Verde Standard Time": "Atlantic/Cape_Verde",
        "Caucasus Standard Time": "Asia/Yerevan",
        "Cen. Australia Standard Time": "Australia/Adelaide",
        "Central America Standard Time": "America/Guatemala",
        "Central Asia Standard Time": "Asia/Almaty",
        "Central Brazilian Standard Time": "America/Cuiaba",
        "Central Europe Standard Time": "Europe/Budapest",
        "Central European Standard Time": "Europe/Warsaw",
        "Central Pacific Standard Time": "Pacific/Guadalcanal",
        "Central Standard Time": "America/Chicago",
        "Central Standard Time (Mexico)": "America/Mexico_City",
        "China Standard Time": "Asia/Shanghai",
        "Dateline Standard Time": "Etc/GMT+12",
        "E. Africa Standard Time": "Africa/Nairobi",
        "E. Australia Standard Time": "Australia/Brisbane",
        "E. Europe Standard Time": "Asia/Nicosia",
        "E. South America Standard Time": "America/Sao_Paulo",
        "Eastern Standard Time": "America/New_York",
        "Egypt Standard Time": "Africa/Cairo",
        "Ekaterinburg Standard Time": "Asia/Yekaterinburg",
        "FLE Standard Time": "Europe/Kiev",
        "Fiji Standard Time": "Pacific/Fiji",
        "GMT Standard Time": "Europe/London",
        "GTB Standard Time": "Europe/Bucharest",
        "Georgian Standard Time": "Asia/Tbilisi",
        "Greenland Standard Time": "America/Godthab",
        "Greenwich Standard Time": "Atlantic/Reykjavik",
        "Hawaiian Standard Time": "Pacific/Honolulu",
        "India Standard Time": "Asia/Calcutta",
        "Iran Standard Time": "Asia/Tehran",
        "Israel Standard Time": "Asia/Jerusalem",
        "Jordan Standard Time": "Asia/Amman",
        "Kaliningrad Standard Time": "Europe/Kaliningrad",
        "Korea Standard Time": "Asia/Seoul",
        "Magadan Standard Time": "Asia/Magadan",
        "Mauritius Standard Time": "Indian/Mauritius",
        "Middle East Standard Time": "Asia/Beirut",
        "Montevideo Standard Time": "America/Montevideo",
        "Morocco Standard Time": "Africa/Casablanca",
        "Mountain Standard Time": "America/Denver",
        "Mountain Standard Time (Mexico)": "America/Chihuahua",
        "Myanmar Standard Time": "Asia/Rangoon",
        "N. Central Asia Standard Time": "Asia/Novosibirsk",
        "Namibia Standard Time": "Africa/Windhoek",
        "Nepal Standard Time": "Asia/Katmandu",
        "New Zealand Standard Time": "Pacific/Auckland",
        "Newfoundland Standard Time": "America/St_Johns",
        "North Asia East Standard Time": "Asia/Irkutsk",
        "North Asia Standard Time": "Asia/Krasnoyarsk",
        "Pacific SA Standard Time": "America/Santiago",
        "Pacific Standard Time": "America/Los_Angeles",
        "Pacific Standard Time (Mexico)": "America/Santa_Isabel",
        "Pakistan Standard Time": "Asia/Karachi",
        "Paraguay Standard Time": "America/Asuncion",
        "Romance Standard Time": "Europe/Paris",
        "Russian Standard Time": "Europe/Moscow",
        "SA Eastern Standard Time": "America/Cayenne",
        "SA Pacific Standard Time": "America/Bogota",
        "SA Western Standard Time": "America/La_Paz",
        "SE Asia Standard Time": "Asia/Bangkok",
        "Samoa Standard Time": "Pacific/Apia",
        "Singapore Standard Time": "Asia/Singapore",
        "South Africa Standard Time": "Africa/Johannesburg",
        "Sri Lanka Standard Time": "Asia/Colombo",
        "Syria Standard Time": "Asia/Damascus",
        "Taipei Standard Time": "Asia/Taipei",
        "Tasmania Standard Time": "Australia/Hobart",
        "Tokyo Standard Time": "Asia/Tokyo",
        "Tonga Standard Time": "Pacific/Tongatapu",
        "Turkey Standard Time": "Europe/Istanbul",
        "US Eastern Standard Time": "America/Indianapolis",
        "US Mountain Standard Time": "America/Phoenix",
        "UTC": "Etc/GMT",
        "UTC+12": "Etc/GMT-12",
        "UTC-02": "Etc/GMT+2",
        "UTC-11": "Etc/GMT+11",
        "Ulaanbaatar Standard Time": "Asia/Ulaanbaatar",
        "Venezuela Standard Time": "America/Caracas",
        "Vladivostok Standard Time": "Asia/Vladivostok",
        "W. Australia Standard Time": "Australia/Perth",
        "W. Central Africa Standard Time": "Africa/Lagos",
        "W. Europe Standard Time": "Europe/Berlin",
        "West Asia Standard Time": "Asia/Tashkent",
        "West Pacific Standard Time": "Pacific/Port_Moresby",
        "Yakutsk Standard Time": "Asia/Yakutsk",
    }
    return lookup.get(s)
