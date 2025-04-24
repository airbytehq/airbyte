#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import time
from datetime import datetime
from typing import Dict, Generator, Optional

from faunadb import _json
from faunadb import query as q
from faunadb.client import FaunaClient
from faunadb.errors import FaunaError, Unauthorized
from faunadb.objects import Ref

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
        # The page size, used in all Paginate() calls.
        self.page_size = conf["page_size"]

        # Configs for how deletions are handled
        self.deletions = DeletionsConfig(conf["deletions"])


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
        "data": q.select("data", doc, {}),
        "ttl": q.select("ttl", doc, None),
    }
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

            # Validate everything else after making sure the database is up.
            try:
                self.client.query(q.now())
            except Exception as e:
                if type(e) is Unauthorized:
                    return fail("Failed to connect to database: Unauthorized")
                else:
                    return fail(f"Failed to connect to database: {e}")

            # Validate our permissions
            try:
                self.client.query(q.paginate(q.collections()))
            except FaunaError:
                return fail("No permissions to list collections")
            try:
                self.client.query(q.paginate(q.indexes()))
            except FaunaError:
                return fail("No permissions to list indexes")

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

    def find_index_for_stream(self, collection: str) -> str:
        """
        Finds the index for the given collection name. This will iterate over all indexes, and find
        one that has the correct source, values, and terms.

        :param collection: The name of the collection to search for.
        """
        page = self.client.query(q.paginate(q.indexes()))
        while True:
            for id in page["data"]:
                try:
                    index = self.client.query(q.get(id))
                except Unauthorized:
                    # If we don't have permissions to read this index, we ignore it.
                    continue
                source = index["source"]
                # Source can be an array, in which case we want to skip this index
                if (
                    type(source) is Ref
                    and source.collection() == Ref("collections")
                    and source.id() == collection
                    # Index must have 2 values and no terms
                    and len(index["values"]) == 2
                    and len(index["terms"]) == 0
                    # Index values must be ts and ref
                    and index["values"][0] == {"field": "ts"}
                    and index["values"][1] == {"field": "ref"}
                ):
                    return index["name"]
            if "after" in page:
                page = self.client.query(q.paginate(q.indexes(), after=page["after"]))
            else:
                break
        raise ValueError(f"Could not find index for stream '{collection}'")

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
            self._setup_client(config)

            # Map all the indexes with the correct values to their collection.
            collections_to_indexes = {}
            page = self.client.query(q.paginate(q.indexes()))
            while True:
                for id in page["data"]:
                    try:
                        index = self.client.query(q.get(id))
                    except Unauthorized:
                        # If we don't have permissions to read this index, we ignore it.
                        continue
                    source = index["source"]
                    # Source can be an array, in which case we want to skip this index
                    if (
                        type(source) is Ref
                        and source.collection() == Ref("collections")
                        # Index must have 2 values and no terms
                        and ("values" in index and len(index["values"]) == 2)
                        and (("terms" in index and len(index["terms"]) == 0) or "terms" not in index)
                        # Index values must be ts and ref
                        and index["values"][0] == {"field": "ts"}
                        and index["values"][1] == {"field": "ref"}
                    ):
                        collections_to_indexes[source.id()] = index
                if "after" in page:
                    page = self.client.query(q.paginate(q.indexes(), after=page["after"]))
                else:
                    break

            page = self.client.query(q.paginate(q.collections()))
            while True:
                for collection in page["data"]:
                    stream_name = collection.id()
                    json_schema = {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "type": "object",
                        "properties": {
                            "ref": {
                                "type": "string",
                            },
                            "ts": {
                                "type": "integer",
                            },
                            "data": {
                                "type": "object",
                            },
                            "ttl": {
                                "type": ["null", "integer"],
                            },
                        },
                    }
                    supported_sync_modes = ["full_refresh"]
                    if stream_name in collections_to_indexes:
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
                if "after" in page:
                    page = self.client.query(q.paginate(q.collections(), after=page["after"]))
                else:
                    break
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

                    index = self.find_index_for_stream(stream_name)
                    logger.info(f"found index '{index}', which will be used to sync '{stream_name}'")
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
                        index,
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
