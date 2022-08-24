#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import time
from datetime import datetime
from typing import Dict, Generator, Optional

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Status,
    SyncMode,
    Type,
)
from airbyte_cdk.sources import Source
from faunadb import _json
from faunadb import query as q
from faunadb.client import FaunaClient
from faunadb.errors import FaunaError, Unauthorized
from faunadb.objects import Ref
from source_fauna.serialize import fauna_doc_to_airbyte


# All config fields. These match the shape of spec.yaml.
class Config:
    def __init__(self, conf):
        # Domain of Fauna connection (localhost, db.fauna.com).
        self.domain = conf["domain"]
        # Port of Fauna connection (8443, 443).
        self.port = conf["port"]
        # Scheme of Fauna connection (https, http).
        self.scheme = conf["scheme"]
        # Secret of a Fauna DB (my-secret).
        self.secret = conf["secret"]
        self.collection = CollectionConfig(conf["collection"])


class CollectionConfig:
    def __init__(self, conf):
        # Name of the collection we are reading from.
        self.name = conf["name"]
        # true or false; do we add a `data` column that mirrors all the data in each document?
        self.data_column = conf["data_column"]
        # Any additional columns the user wants.
        self.additional_columns = [Column(x) for x in conf.get("additional_columns", [])]
        # The page size, used in all Paginate() calls.
        self.page_size = conf["page_size"]
        # Index name used in read_updates. Default to empty string
        self.index = conf.get("index", "")

        # Configs for how deletions are handled
        self.deletions = DeletionsConfig(conf["deletions"])


class Column:
    def __init__(self, conf):
        # The name of this column. This is the name that will appear in the destination.
        self.name = conf["name"]
        # The path of the value within fauna. This is an array of strings.
        self.path = conf["path"]
        # The type of the value used in Airbyte. This will be used by most destinations
        # as the column type. This is not validated at all!
        self.type = conf["type"]
        # If true, then the path above must exist in every document.
        self.required = conf["required"]
        # The format and airbyte_type are extra typing fields. Documentation:
        # https://docs.airbyte.com/understanding-airbyte/supported-data-types/
        self.format = conf.get("format")
        self.airbyte_type = conf.get("airbyte_type")


class DeletionsConfig:
    def __init__(self, conf):
        self.mode = conf["deletion_mode"]
        self.column = conf.get("column")


def expand_column_query(conf: CollectionConfig, value):
    """
    Returns a query on Fauna document producing an object according to the user's configuraiton.

    Using the given CollectionConfig, this will add every additional column that is listed into
    the resulting object. This will also add ref and ts, and data if conf.data_column is
    enabled.

    :param conf: the CollectionConfig
    :param value: a Fauna expression, which will produce a Ref to the document in question
    :return: a Fauna expression for extracting the object
    """
    doc = q.var("document")
    obj = {
        "ref": q.select(["ref", "id"], doc),
        "ts": q.select("ts", doc),
    }
    if conf.data_column:
        obj["data"] = q.select("data", doc)
    for column in conf.additional_columns:
        if column.required:
            obj[column.name] = q.select(
                column.path,
                doc,
                q.abort(
                    q.format(
                        f"The path {column.path} does not exist in document Ref(%s, collection=%s)",
                        q.select(["ref", "id"], doc),
                        q.select(["ref", "collection", "id"], doc),
                    )
                ),
            )
        else:
            # If not required, default to None
            obj[column.name] = q.select(column.path, doc, None)
    return q.let(
        {"document": q.get(value)},
        obj,
    )


class SourceFauna(Source):
    def _setup_client(self, config):
        self.client = FaunaClient(
            secret=config.secret,
            domain=config.domain,
            port=config.port,
            scheme=config.scheme,
        )

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to Fauna.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """

        config = Config(config)

        def fail(message: str) -> AirbyteConnectionStatus:
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message=message,
            )

        try:
            self._setup_client(config)

            # STEP 1: Validate as much as we can before connecting to the database

            # Collection config, which has all collection-specific config fields.
            conf = config.collection

            # Make sure they didn't choose an duplicate or invalid column names.
            column_names = {}
            for column in conf.additional_columns:
                # We never allow a custom `data` column, as they might want to enable the
                # data column later.
                if column.name == "data" or column.name == "ref" or column.name == "ts":
                    return fail(f"Additional column cannot have reserved name '{column.name}'")
                if column.name in column_names:
                    return fail(f"Additional column cannot have duplicate name '{column.name}'")
                column_names[column.name] = ()

            # STEP 2: Validate everything else after making sure the database is up.
            try:
                self.client.query(q.now())
            except Exception as e:
                if type(e) is Unauthorized:
                    return fail("Failed to connect to database: Unauthorized")
                else:
                    return fail(f"Failed to connect to database: {e}")

            # Validate the collection exists
            collection = conf.name
            try:
                self.client.query(q.paginate(q.documents(q.collection(collection)), size=1))
            except FaunaError:
                return fail(f"Collection '{collection}' does not exist")

            # If they entered an index, make sure it's correct
            if conf.index != "":
                res = self._validate_index(conf.name, conf.index)
                if res is not None:
                    return fail(res)

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {e}")

    def _validate_index(self, collection: str, index: str) -> Optional[str]:
        # Validate that the index exists
        if not self.client.query(q.exists(q.index(index))):
            return f"Index '{index}' does not exist"

        # Validate the index source
        actual_source = self.client.query(q.select("source", q.get(q.index(index))))
        expected_source = Ref(collection, Ref("collections"))
        if actual_source != expected_source:
            return f"Index '{index}' should have source '{collection}', but it has source '{actual_source.id()}'"

        # If the index has no values, we return `[]`
        actual_values = self.client.query(q.select("values", q.get(q.index(index)), []))
        expected_values = [
            {"field": "ts"},
            {"field": "ref"},
        ]
        # If the index has extra values, that is fine. We just need the first two values to
        # be `ts` and `ref`. Also note that python will not crash if 2 is out of range,
        # instead [:2] will just return an empty list. The first two values must match to
        # guarantee the expected sort order.
        if actual_values[:2] != expected_values:
            return f"Index should have values {expected_values}, but it has values {actual_values}"

        # All above checks passed, so it's valid.
        return None

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        """
        Returns an AirbyteCatalog representing the available streams and fields in the user's connection to Fauna.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteCatalog is an object describing a list of all available streams in this Fauna source.
            A stream is an AirbyteStream object that includes:
            - its stream name (or collection name in the case of Fauna)
            - json_schema providing the specifications of expected schema for this stream (a list of fields described
            by their names and types)
        """

        config = Config(config)
        streams = []

        try:
            # Check if we entered an index. This will already be validated by check().
            can_sync_incremental = config.collection.index != ""

            # We only support a single stream. This is limiting, but makes things a lot simpler.
            conf = config.collection
            stream_name = conf.name
            properties = {
                "ref": {
                    "type": "string",
                },
                "ts": {
                    "type": "integer",
                },
            }
            if conf.data_column:
                properties["data"] = {"type": "object"}
            for column in conf.additional_columns:
                column_object = {}

                # This is how we specify optionals, according to the docs:
                # https://docs.airbyte.com/understanding-airbyte/supported-data-types/#nulls
                if column.required:
                    column_object["type"] = column.type
                else:
                    column_object["type"] = ["null", column.type]

                # Extra fields, for more formats. See the docs:
                # https://docs.airbyte.com/understanding-airbyte/supported-data-types/
                if column.format is not None:
                    column_object["format"] = column.format
                if column.airbyte_type is not None:
                    column_object["airbyte_type"] = column.airbyte_type

                properties[column.name] = column_object
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": properties,
            }
            supported_sync_modes = ["full_refresh"]
            if can_sync_incremental:
                supported_sync_modes.append("incremental")
            streams.append(
                AirbyteStream(
                    name=stream_name,
                    json_schema=json_schema,
                    supported_sync_modes=supported_sync_modes,
                    source_defined_cursor=True,
                    default_cursor_field=["ts"],
                )
            )
        except Exception as e:
            logger.error(f"error in discover: {e}")
            return AirbyteCatalog(streams=[])

        return AirbyteCatalog(streams=streams)

    def find_ts(self, config) -> int:
        # TODO: Config-defined timestamp here
        return self.client.query(q.to_micros(q.now()))

    def find_emitted_at(self) -> int:
        # Returns now, in microseconds. This is a seperate function, so that it is easy
        # to replace in unit tests.
        return int(time.time() * 1000)

    def read_removes(
        self, logger, stream: ConfiguredAirbyteStream, conf: CollectionConfig, state: dict[str, any], deletion_column: str
    ) -> Generator[any, None, None]:
        """
        This handles all additions and deletions, not updates.

        :param logger: The Airbyte logger.
        :param stream: The configured airbyte stream, which is only used in logging.
        :param conf: The configured collection options. This is used for page size and expand_column_query.
        :param state: The state of this stream. This should be a black-box to the caller.
        :param deletion_column: The column to put the 'deleted_at' field in.
        :return: A generator which will produce a number data fields for an AirbyteRecordMessage.
        """

        stream_name = stream.stream.name
        logger.info(f"reading add/removes for stream {stream_name}")

        if "after" in state:
            # If the last query failed, we will have stored the after token used there, so we can
            # resume more reliably.
            after = _json.parse_json(state["after"])
        else:
            # If the last query succeeded, then we will fallback to the ts of the most recent
            # document. Here we are creating an after token! However, because we are passing it
            # to Paginate over Events, the docs specifically call out that we can pass a timestamp
            # for the 'after' value, and that will give us the events after a certain time.
            after = {
                "ts": state.get("ts", 0),
                "action": "remove",
            }
            if "ref" in state and state["ref"] != "":
                after["resource"] = q.ref(q.collection(stream_name), state["ref"])

        def setup_query(after):
            paginate_section = q.paginate(
                q.documents(q.collection(stream_name)),
                events=True,
                after=after,
                size=conf.page_size,
            )
            # Filter for only removes
            paginate_section = q.filter_(
                q.lambda_("x", q.equals(q.select(["action"], q.var("x")), "remove")),
                paginate_section,
            )
            return q.map_(
                q.lambda_(
                    "x",
                    {
                        "ref": q.select("document", q.var("x")),
                        "ts": q.select("ts", q.var("x")),
                    },
                ),
                paginate_section,
            )

        events = self.client.query(setup_query(after=after))
        # These are the new state values. It will be written to the state after we are done emitting
        # documents.
        #
        # These are inclusive, so we will skip a document with this ref and ts if we find it next
        # time.
        new_ts = state.get("ts", 0)
        new_ref = state.get("ref", "")
        while True:
            if "after" not in events and len(events["data"]) > 0:
                new_ref = events["data"][-1]["ref"].id()
                new_ts = events["data"][-1]["ts"]
            for event in events["data"]:
                ref = event["ref"].id()
                ts = event["ts"]

                # We don't want duplicate documents, so we skip this if it was the one we emitted
                # last time.
                if ref == state.get("ref") and ts == state.get("ts"):
                    continue

                # Crash after a specific document. Used in manual testing.
                # if int(ref) > 337014929908302336:
                #     raise ValueError("ahh")

                data_obj = {
                    "ref": ref,
                    "ts": ts,
                    # Put a timestamp in this column, to show that the document has been deleted
                    deletion_column: datetime.utcfromtimestamp(ts / 1_000_000).isoformat(),
                }
                logger.info(f"emitting object {data_obj}")
                yield data_obj

            if "after" in events:
                # Set this before running the query, so that if it fails, we can retry this same
                # query next time.
                state["after"] = _json.to_json(events["after"])
                events = self.client.query(setup_query(after=events["after"]))
            else:
                # Make sure we don't try to use this after token, as we've read to the end of this
                # Paginate.
                if "after" in state:
                    del state["after"]
                # Now that we are done, write the new ts field. If we were to fail while `yield`ing
                # above, then our state wouldn't be updated, so we won't skip documents.
                state["ts"] = new_ts
                state["ref"] = new_ref
                break

    def read_updates(
        self, logger, stream: ConfiguredAirbyteStream, conf: CollectionConfig, state: Dict[str, any], index: str, page_size: int
    ) -> Generator[any, None, None]:
        """
        This handles all document creations/updates. It does not handle document deletions.

        The state has 3 optional fields:
        `ts`:
        This is the `ts` of the last document emitted from the previous query.
        `ref`:
        This is the `ref` id of the last document emitted from the previous query.
        `after`:
        This is a wire-protocol serialized after token from Paginate(). This
        will only be set if the last query failed. This is passed to Paginate()
        in order to resume at the correct location.

        In the happy case, only `ts` and `ref` will be set.
        """
        stream_name = stream.stream.name
        logger.info(f"reading document updates for stream {stream_name}")

        if "after" in state:
            # If the last query failed, we will have stored the after token used there, so we can
            # resume more reliably.
            after = _json.parse_json(state["after"])
        else:
            # If there is no after token, the last query was successful.
            after = None

        # If we have a broken state, or an incomplete state, this will build the correct range min.
        range_min = [state.get("ts", 0)]
        if "ref" in state:
            range_min.append(q.ref(q.collection(stream_name), state.get("ref", "")))

        def get_event_values(expr: q._Expr) -> q._Expr:
            return q.map_(
                q.lambda_("x", expand_column_query(conf, q.select(1, q.var("x")))),
                expr,
            )

        modified_documents = self.client.query(
            get_event_values(
                q.paginate(
                    q.range(
                        q.match(q.index(index)),
                        range_min,  # use the min we got above
                        [],  # no max
                    ),
                    size=page_size,
                    after=after,
                )
            )
        )
        # These are the new state values. It will be written to the state after we are done emitting
        # documents.
        #
        # These are inclusive, so we will skip a document with this ref and ts if we find it next
        # time.
        new_ts = state.get("ts", 0)
        new_ref = state.get("ref", "")
        while True:
            if "after" not in modified_documents and len(modified_documents["data"]) > 0:
                new_ref = modified_documents["data"][-1]["ref"]
                new_ts = modified_documents["data"][-1]["ts"]
            for doc in modified_documents["data"]:
                # We don't want duplicate documents, so we skip this if it was the one we emitted
                # last time.
                if doc["ref"] == state.get("ref") and doc["ts"] == state.get("ts"):
                    continue
                yield doc
            if "after" in modified_documents:
                state["after"] = _json.to_json(modified_documents["after"])
                modified_documents = self.client.query(
                    get_event_values(
                        q.paginate(
                            q.range(
                                q.match(q.index(index)),
                                range_min,
                                [],
                            ),
                            size=page_size,
                            after=modified_documents["after"],
                        )
                    )
                )
            else:
                # Completed successfully, so we remove the after token, and update the ts.
                if "after" in state:
                    del state["after"]
                # Now that we are done, write the new ts field. If we were to fail while `yield`ing
                # above, then our state wouldn't be updated, so we won't skip documents.
                state["ts"] = new_ts
                state["ref"] = new_ref
                break

    def read_all(self, logger, stream: ConfiguredAirbyteStream, conf: CollectionConfig, state: dict) -> Generator[any, None, None]:
        """
        Reads all documents. The `state` must have a field of 'full_sync_cursor', which is a dict
        containing elements: `ts` and `ref`.

        The `ts` field must always be present. It is the value use in `At` for the whole query.

        The `ref` field is optional. If present, it will be used to resume a paginate. This should
        only be present when resuming a failed sync. If not present, the `Paginate` will list every
        document.
        """
        # This handles fetching all documents. Used in full sync.
        stream_name = stream.stream.name

        after = state["full_sync_cursor"].get("after")
        if after is not None:
            # Deserialize the after token from the wire protocol
            after = _json.parse_json(after)
            logger.info(f"using after token {after}")
        else:
            logger.info("no after token, starting from beginning")

        ts = state["full_sync_cursor"]["ts"]

        def get_event_values(expr: q._Expr) -> q._Expr:
            return q.at(
                ts,
                q.map_(
                    q.lambda_("x", expand_column_query(conf, q.var("x"))),
                    expr,
                ),
            )

        all_documents = self.client.query(
            get_event_values(
                q.paginate(
                    q.documents(q.collection(stream_name)),
                    size=conf.page_size,
                    after=after,
                )
            )
        )
        while True:
            yield from all_documents["data"]
            if "after" in all_documents:
                # Serialize the after token to the wire protocol
                state["full_sync_cursor"]["after"] = _json.to_json(all_documents["after"])

                # if this query crashes, the state will have this after token stored.
                # therefore, on the next retry, this same query will be performend,
                # which is what we want to have happened.
                all_documents = self.client.query(
                    get_event_values(
                        q.paginate(
                            q.documents(q.collection(stream_name)),
                            size=conf.page_size,
                            after=all_documents["after"],
                        )
                    )
                )
            else:
                break

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
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

        config = Config(config)
        logger.info(f"state: {state}")

        def make_message(stream_name, data_obj) -> AirbyteMessage:
            return AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    stream=stream_name,
                    data=fauna_doc_to_airbyte(data_obj),
                    emitted_at=self.find_emitted_at(),
                ),
            )

        try:
            self._setup_client(config)

            for stream in catalog.streams:
                stream_name = stream.stream.name
                if stream.sync_mode == SyncMode.full_refresh:
                    logger.info(f"syncing stream '{stream_name}' with full_refresh")

                    if state[stream_name].get("full_sync_cursor", {}).get("ts") is None:
                        # No sync yet, so determine `ts`
                        logger.info("this is the start of a sync (no cursor has been set)")
                        state[stream_name]["full_sync_cursor"] = {"ts": self.find_ts(config)}
                    else:
                        logger.info("this is the middle of a sync (a cursor has been set)")

                    logger.info(f"syncing at ts {state[stream_name]['full_sync_cursor']['ts']}")

                    # Now, if we crash, we will emit this state. Airbyte will retry the sync, and
                    # use the state that was first passed to this function. This means the retry
                    # will not be able to resume correctly, and it may choose a new `ts` field.
                    # We cannot do anything about this behavior.
                    #
                    # If the user manually tries to sync again, after the sync failed, then this
                    # state will be used, and we can resume.
                    for data_obj in self.read_all(logger, stream, config.collection, state=state[stream_name]):
                        yield make_message(stream_name, data_obj)

                    # We finished, so we clear the state, so that the next sync will start at the
                    # beginning.
                    del state[stream_name]["full_sync_cursor"]
                    yield AirbyteMessage(
                        type=Type.STATE,
                        state=AirbyteStateMessage(
                            data=state,
                            emitted_at=self.find_emitted_at(),
                        ),
                    )
                elif stream.sync_mode == SyncMode.incremental:
                    logger.info(f"syncing stream '{stream_name}' with incremental")
                    if stream_name not in state:
                        state[stream_name] = {}

                    read_deletions = config.collection.deletions.mode == "deleted_field"

                    # Read removals
                    if read_deletions:
                        if "remove_cursor" not in state[stream_name]:
                            state[stream_name]["remove_cursor"] = {}
                        for data_obj in self.read_removes(
                            logger,
                            stream,
                            config.collection,
                            state[stream_name]["remove_cursor"],
                            deletion_column=config.collection.deletions.column,
                        ):
                            yield make_message(stream_name, data_obj)
                    else:
                        logger.info("skipping collection events (no deletions needed)")
                    # Read adds/updates
                    if "updates_cursor" not in state[stream_name]:
                        state[stream_name]["updates_cursor"] = {}
                    for data_obj in self.read_updates(
                        logger,
                        stream,
                        config.collection,
                        state[stream_name]["updates_cursor"],
                        config.collection.index,
                        config.collection.page_size,
                    ):
                        yield make_message(stream_name, data_obj)
                    # Yield our state
                    yield AirbyteMessage(
                        type=Type.STATE,
                        state=AirbyteStateMessage(
                            data=state,
                            emitted_at=self.find_emitted_at(),
                        ),
                    )
                else:
                    logger.error(f"could not sync stream '{stream.stream.name}', invalid sync_mode: {stream.sync_mode}")

        except Exception as e:
            yield AirbyteMessage(
                type=Type.STATE,
                state=AirbyteStateMessage(
                    data=state,
                    emitted_at=self.find_emitted_at(),
                ),
            )
            logger.error(e)
            raise
