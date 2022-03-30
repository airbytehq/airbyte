#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import copy
import dataclasses
import fnmatch
import logging
import itertools
import re
import threading
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Iterator, Generic, TypeVar, cast, Dict, Union
from typing_extensions import Protocol
from urllib.parse import urlparse, parse_qs

import dateutil.parser
import requests
from airbyte_cdk.models import SyncMode, ConfiguredAirbyteCatalog, AirbyteMessage
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth, AuthBase

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""

logger = logging.getLogger("airbyte")

# Not including implementation classes since those are likely to change over time and based on installed plugins.
# Examples:
#   - "io.jenkins.blueocean.service.embedded.rest.PipelineFolderImpl"
#   - "io.jenkins.blueocean.rest.impl.pipeline.MultiBranchPipelineImpl"
BASE_FOLDER_CLASS = "com.cloudbees.hudson.plugins.folder.AbstractFolder"

MULTIBRANCH_CLASS = {"jenkins.branch.MultiBranchProject", "io.jenkins.blueocean.rest.model.BlueBranch"}

# TODO: Should this be "org.jenkinsci.plugins.workflow.job.WorkflowJob" instead?
JOB_CLASS = "hudson.model.Job"

HTTP_ADAPTER = HTTPAdapter(pool_connections=1, pool_maxsize=1, max_retries=3)

T = TypeVar("T")


class CachingIterable(Generic[T], Iterator[T]):
    def __init__(self, iterable: Iterator[T]):
        self._real_iter = iter(iterable)
        self._done = False
        self._cache = []
        self.lock = threading.Lock()

    def __iter__(self):
        if self._done:
            return iter(self._cache)
        return itertools.chain(self._cache, self._remaining())

    def __next__(self) -> T:
        if self._done:
            raise StopIteration()
        try:
            next_val = next(self._real_iter)
            self._cache.append(next_val)
            return next_val
        except StopIteration as e:
            self._done = True
            raise e

    def _remaining(self) -> Iterator[T]:
        for val in self._real_iter:
            self._cache.append(val)
            yield val
        self._done = True


class StreamProtocol(Protocol):
    def stream_slices(
            self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]: ...

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]: ...

    @property
    def url_base(self) -> str: ...


class JenkinsStream(HttpStream, ABC):
    url_base = "https://example.com/jenkins/"
    page_size = 500

    def __init__(self, url_base: str, authenticator: AuthBase) -> None:
        url_base = url_base.rstrip("/")
        if not url_base.endswith("/blue/rest"):
            url_base += "/blue/rest"
        url_base += "/"
        self.url_base = url_base
        self._jenkins_auth = authenticator
        super().__init__(authenticator)

        self._session.mount("https://", HTTP_ADAPTER)
        self._session.mount("http://", HTTP_ADAPTER)

    @lru_cache()
    def resolve_classes(self, class_name: str) -> List[str]:
        class_url = f"{self.url_base}/classes/{class_name}/"
        response = self._session.get(class_url)
        response.raise_for_status()
        return response.json().get("classes", [])

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        # If errors are turned off we might have 404 errors. They are HTML, don't try to parse them as JSON.
        if 400 <= response.status_code < 600:
            return
        yield from response.json()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # If we hit an error, stop paging.
        if 400 <= response.status_code < 600:
            return None
        # Only page if we got fewer than the expected number of results.
        if len(response.json()) < self.page_size:
            return None
        next_url = response.headers["Link"].split(";")[0].lstrip("<").rstrip(">")
        next_url = self.url_base + next_url
        new_params = parse_qs(urlparse(next_url).query)
        return new_params

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"start": 0, "limit": self.page_size}
        if next_page_token is not None:
            params.update(next_page_token)
        return params


class Organizations(JenkinsStream):
    """
    The Jenkins Blue Ocean internals supports multiple organizations, but in practice only uses one, "jenkins".
    """
    primary_key = "name"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"organizations/"


class ParentStreamMixin(IncrementalMixin):
    cache_records = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = {}
        self._initial_state = None
        self._cache_by_sync_mode = {}

    @property
    @abstractmethod
    def sync_mode(self) -> SyncMode:
        """
        Return the configured sync mode of the stream.
        """

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @property
    def initial_state(self) -> MutableMapping[str, Any]:
        return self._initial_state or {}

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        # Save off the initial state as soon as it is set.
        if self._initial_state is None:
            self._initial_state = copy.deepcopy(value)
        self._state = value

    def read_records_from_initial_state(self, sync_mode: SyncMode):
        # Should not adjust the state variable at all.
        if not self.cache_records:
            return self._read_records_from_initial_state(sync_mode)
        if self.cache_records and sync_mode not in self._cache_by_sync_mode:
            # TODO: move CachingIterable to a decorator
            self._cache_by_sync_mode[sync_mode] = CachingIterable(self._read_records_from_initial_state(sync_mode))
        return self._cache_by_sync_mode[sync_mode]

    def _read_records_from_initial_state(self: Union[StreamProtocol, 'ParentStreamMixin'], sync_mode: SyncMode):
        for stream_slice in self.stream_slices(sync_mode=sync_mode, stream_state=self.initial_state):
            yield from self.read_records(sync_mode=sync_mode, stream_slice=stream_slice, stream_state=self.initial_state)


class Pipelines(ParentStreamMixin, JenkinsStream):
    """
    Non-incremental stream of Pipelines.
    """
    primary_key = "fullName"
    use_cache = True
    sync_mode = SyncMode.full_refresh

    def __init__(
        self,
        organizations: Iterable[str],
        pipelines: Iterable[str],
        exclude_multibranch: bool,
        sync_mode: SyncMode,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._organizations = organizations
        self._pipelines = [re.compile(fnmatch.translate(p)) for p in pipelines]
        self.sync_mode = sync_mode
        self._exclude_multibranch = exclude_multibranch

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for org in self._organizations:
            yield {"organization": org}

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"search/"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            "q": f"type:pipeline;organization:{stream_slice['organization']}",
            "start": 0,
            "limit": self.page_size,
        }
        if next_page_token is not None:
            params.update(next_page_token)
        return params

    def read_records(self, sync_mode: SyncMode, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(sync_mode, *args, **kwargs):
            full_name = record["fullName"]
            pipeline_class = record["_class"]
            if self._exclude_multibranch and any(c in MULTIBRANCH_CLASS for c in self.resolve_classes(pipeline_class)):
                continue
            if any(p.match(full_name) for p in self._pipelines):
                yield record


@dataclasses.dataclass
class OrganizationPipelines:
    organization: str
    pipelines: List[str]


class CachingSubStream(JenkinsStream, ABC):
    use_cache = True

    def __init__(self, parent: ParentStreamMixin, **kwargs):
        """
        :param parent: should be the instance of HttpStream class
        """
        super().__init__(**kwargs)
        self.parent = parent

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # Differs from HttpSubStream in that we try to use the sync_mode of the parent when we are running in
        # incremental mode, not always full_refresh.
        parent_sync_mode = self.parent.sync_mode
        if sync_mode == SyncMode.full_refresh:
            parent_sync_mode = SyncMode.full_refresh

        for record in self.parent.read_records_from_initial_state(parent_sync_mode):
            yield {"parent": record}


def normalize_date_string(value: str) -> str:
    return dateutil.parser.parse(value).replace(tzinfo=None).isoformat()


class Runs(ParentStreamMixin, CachingSubStream):
    """
    Stream for pulling Runs.

    This needs to hit the /runs/ endpoint for every pipeline that's being exported. The Stages and Steps streams also need
    this information to know what should be exported.

    There is a search endpoint in Jenkins, but it didn't seem to support returning runs across pipelines very reliably.
        /blue/rest/search/?q=type:run
    """
    primary_key = ["pipelineFullName", "id"]

    # TODO: change to endTime?
    cursor_field = "startTime"

    sync_mode = SyncMode.full_refresh

    # Runs are often pruned by Jenkins, resulting in 404 errors.
    raise_on_http_errors = False

    def __init__(self, parent: Pipelines, start_date: str, sync_mode: SyncMode, **kwargs) -> None:
        super().__init__(parent=parent, **kwargs)
        self._start_date = normalize_date_string(start_date or "1970-01-01T00:00:00Z")
        self.sync_mode = sync_mode

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        organization = stream_slice["parent"]["organization"]
        pipeline = stream_slice["parent"]["fullName"]
        return f"organizations/{organization}/pipelines/{pipeline}/runs/"

    @staticmethod
    def _state_key(stream_slice: Mapping[str, Any]) -> str:
        if stream_slice is None:
            raise ValueError("Invalid slice")
        organization = stream_slice["parent"]["organization"]
        pipeline = stream_slice["parent"]["fullName"]
        return f"{organization}/{pipeline}"

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for stream_slice in super().stream_slices(sync_mode, cursor_field, stream_state):
            # Filter out parents that aren't actual Jobs (e.g. folders, multi-branch builds).
            parent_class = stream_slice["parent"]["_class"]
            if JOB_CLASS not in self.resolve_classes(parent_class):
                continue

            # Use the "latestRun" information to skip pipelines that haven't been run.
            start_date_str = stream_state.get(self._state_key(stream_slice), {}).get(self.cursor_field) or self._start_date
            run_start_date = normalize_date_string(start_date_str)
            latest_run = stream_slice["parent"]["latestRun"] or {}
            latest_start_date = normalize_date_string(latest_run.get(self.cursor_field) or self._start_date)
            if latest_start_date > run_start_date:
                yield stream_slice

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        start_date = normalize_date_string(stream_state.get(self._state_key(stream_slice), {}).get(self.cursor_field) or self._start_date)

        max_state = start_date

        # Process runs in reversed order so we can update the state accurately.
        records = reversed(list(super().read_records(sync_mode, cursor_field, stream_slice, stream_state)))
        for record in records:
            # Runs can be queued but not started yet. For now, we ignore runs that haven't started.
            run_start_time = normalize_date_string(record.get(self.cursor_field) or self._start_date)
            if run_start_time > start_date:
                record = cast(Dict[str, Any], record)
                record["pipelineFullName"] = stream_slice["parent"]["fullName"]
                yield record

            # Keep track of the max date we see. That will be the final state after success on this slice.
            current_state = run_start_time or max_state
            max_state = max(current_state, max_state)

        # Update the state when the slice is completed.
        self.state[self._state_key(stream_slice)] = {self.cursor_field: max_state}


class Nodes(ParentStreamMixin, CachingSubStream):
    primary_key = ["pipelineFullName", "runId", "id"]
    sync_mode = SyncMode.full_refresh

    # Runs are often pruned by Jenkins, resulting in 404 errors.
    raise_on_http_errors = False

    # Doesn't actually use the state or the cursor. Incremental is driven by having incremental set on the Runs
    # parent stream. Incremental on nodes alone would be expensive to perform.
    cursor_field = "id"

    def __init__(self, parent: Runs, start_date: str, sync_mode: SyncMode, **kwargs) -> None:
        super().__init__(parent=parent, **kwargs)
        self.sync_mode = sync_mode
        self._start_date = normalize_date_string(start_date or "1970-01-01T00:00:00Z")

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        organization = stream_slice["parent"]["organization"]
        pipeline = stream_slice["parent"]["pipelineFullName"]
        run_id = stream_slice["parent"]["id"]
        url = f"organizations/{organization}/pipelines/{pipeline}/runs/{run_id}/nodes/"
        return url

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        state_field = "startTime"
        start_date = normalize_date_string(stream_state.get(self._state_key(stream_slice), {}).get(state_field) or self._start_date)
        max_state = start_date

        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            start_time = normalize_date_string(record.get(state_field) or self._start_date)
            if start_time > start_date:
                # Set the pipelineFullName as an FK to the pipelines relation.
                record = cast(Dict[str, Any], record)
                record["organization"] = stream_slice["parent"]["organization"]
                record["pipelineFullName"] = stream_slice["parent"]["pipelineFullName"]
                record["runId"] = stream_slice["parent"]["id"]
                yield record

            current_state = start_time or max_state
            max_state = max(current_state, max_state)
        self.state[self._state_key(stream_slice)] = {state_field: max_state}

    @staticmethod
    def _state_key(stream_slice: Mapping[str, Any]) -> str:
        if stream_slice is None:
            raise ValueError("Invalid slice")
        # TODO: Add organization?
        pipeline = stream_slice["parent"]["pipelineFullName"]
        return pipeline


class Steps(IncrementalMixin, CachingSubStream):
    # Step ids are unique within a run, not only for within a node.
    primary_key = ["pipelineFullName", "runId", "id"]

    # Runs are often pruned by Jenkins, resulting in 404 errors.
    raise_on_http_errors = False

    # Doesn't actually use the state or the cursor. Incremental is driven by having incremental set on the Runs
    # parent stream. Incremental on nodes alone would be expensive to perform.
    cursor_field = "id"
    state = {}

    def __init__(self, parent: Nodes, start_date: str, sync_mode: SyncMode, **kwargs) -> None:
        super().__init__(parent=parent, **kwargs)
        self.sync_mode = sync_mode
        self._start_date = normalize_date_string(start_date or "1970-01-01T00:00:00Z")

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        organization = stream_slice["parent"]["organization"]
        pipeline = stream_slice["parent"]["pipelineFullName"]
        run_id = stream_slice["parent"]["runId"]
        node_id = stream_slice["parent"]["id"]
        url = f"organizations/{organization}/pipelines/{pipeline}/runs/{run_id}/nodes/{node_id}/steps/"
        return url

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        state_field = "startTime"
        start_date = normalize_date_string(stream_state.get(self._state_key(stream_slice), {}).get(state_field) or self._start_date)
        max_state = start_date

        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            start_time = normalize_date_string(record.get(state_field) or self._start_date)
            if start_time > start_date:
                # Set the pipelineFullName as an FK to the pipelines relation.
                record = cast(Dict[str, Any], record)
                record["organization"] = stream_slice["parent"]["organization"]
                record["pipelineFullName"] = stream_slice["parent"]["pipelineFullName"]
                record["runId"] = stream_slice["parent"]["runId"]
                record["nodeId"] = stream_slice["parent"]["id"]
                yield record

            current_state = start_time or max_state
            max_state = max(current_state, max_state)
        self.state[self._state_key(stream_slice)] = {state_field: max_state}

    @staticmethod
    def _state_key(stream_slice: Mapping[str, Any]) -> str:
        if stream_slice is None:
            raise ValueError("Invalid slice")
        # TODO: Add organization?
        pipeline = stream_slice["parent"]["pipelineFullName"]
        return pipeline


# Source
class SourceJenkinsBlue(AbstractSource):
    stream_order = ["organizations", "pipelines", "runs", "nodes", "steps"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._streams: List[Stream] = []

    @staticmethod
    def _generate_orgs(url_base: str, authenticator: AuthBase) -> List[str]:
        orgs = Organizations(url_base=url_base, authenticator=authenticator)
        org_names = [org["name"] for org in orgs.read_records(sync_mode=SyncMode.full_refresh)]
        return org_names

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            url_base = config.get("base_url", "")
            username = config.get("username")
            api_token = config.get("api_token")
            auth = HTTPBasicAuth(username=username, password=api_token)
            orgs = Organizations(url_base=url_base, authenticator=auth)
            next(iter(orgs.read_records(sync_mode=SyncMode.full_refresh)), None)
        except Exception as e:
            return False, e
        return True, None

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: MutableMapping[str, Any] = None,
    ) -> Iterator[AirbyteMessage]:

        # Need to know the sync mode of all streams.
        self._streams = self._build_streams(config, catalog)

        yield from super().read(logger, config, catalog, state)

    def read_catalog(self, catalog_path: str) -> ConfiguredAirbyteCatalog:
        catalog = super().read_catalog(catalog_path=catalog_path)

        # Process the streams in our desired order.
        ordered_streams = sorted(catalog.streams, key=lambda s: self.stream_order.index(s.stream.name))
        catalog.streams = ordered_streams

        return catalog

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # During discover, we don't get a catalog.
        if not self._streams:
            self._streams = self._build_streams(config)
        return self._streams

    def _build_streams(
        self,
        config: Mapping[str, Any],
        catalog: Optional[ConfiguredAirbyteCatalog] = None,
    ) -> List[Stream]:
        # Used to reduce number of requests when using incremental.
        sync_modes = {}
        if catalog is not None:
            sync_modes = {s.stream.name: s.sync_mode for s in catalog.streams}

        url_base = config.get("base_url", "")
        username = config.get("username")
        api_token = config.get("api_token")
        start_date = config.get("start_date").replace("Z", ".000+0000")  # Match the Jenkins date format.
        pipelines = (config.get("pipelines") or "*").split()
        exclude_multibranch = config.get("exclude_multibranch", True)
        authenticator = HTTPBasicAuth(username=username, password=api_token)

        common_args = {"url_base": url_base, "authenticator": authenticator}

        org_names = self._generate_orgs(url_base, authenticator)

        pipelines_stream = Pipelines(
            organizations=org_names,
            pipelines=pipelines,
            exclude_multibranch=exclude_multibranch,
            sync_mode=sync_modes.get("pipelines", SyncMode.full_refresh),
            **common_args,
        )
        runs_stream = Runs(
            parent=pipelines_stream,
            start_date=start_date,
            sync_mode=sync_modes.get("runs", SyncMode.full_refresh),
            **common_args,
        )
        nodes_stream = Nodes(
            parent=runs_stream,
            start_date=start_date,
            sync_mode=sync_modes.get("nodes", SyncMode.full_refresh),
            **common_args,
        )

        streams = [
            Organizations(**common_args),
            pipelines_stream,
            runs_stream,
            nodes_stream,
            Steps(
                parent=nodes_stream,
                start_date=start_date,
                sync_mode=sync_modes.get("steps", SyncMode.full_refresh),
                **common_args,
            )
        ]

        # Emit the streams in our desired order, even though the server ignores that.
        streams = sorted(streams, key=lambda s: self.stream_order.index(s.name))
        return streams
