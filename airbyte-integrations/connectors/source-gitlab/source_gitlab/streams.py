#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from abc import ABC
from typing import Any, Iterable, Mapping, Optional, MutableMapping, List, Dict

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils import casing


class GitlabStream(HttpStream, ABC):
    primary_key = "id"
    stream_base_params = {}
    flatten_id_keys = []
    flatten_list_keys = []
    page = 1
    per_page = 30

    def __init__(self, api_url: str, **kwargs):
        super().__init__(**kwargs)
        self.api_url = api_url

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"page": self.page, "per_page": self.per_page}
        if next_page_token:
            params.update(next_page_token)
        params.update(self.stream_base_params)
        return params

    @property
    def url_base(self) -> str:
        return f"https://{self.api_url}//api/v4/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_data = response.json()
        if isinstance(response_data, dict):
            return None
        if len(response_data) == self.per_page:
            self.page += 1
            return {"page": self.page}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_data = response.json()
        if isinstance(response_data, list):
            for record in response_data:
                yield self.transform(record, **kwargs)
        elif isinstance(response_data, dict):
            yield self.transform(response_data, **kwargs)
        else:
            Exception("TODO")

    def transform(self, record: Dict[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs):
        for key in self.flatten_id_keys:
            self._flatten_id(record, key)

        for key in self.flatten_list_keys:
            self._flatten_list(record, key)

        return record

    def _flatten_id(self, record: Dict[str, Any], target: str):
        if record.get(target):
            record[target + '_id'] = record.pop(target, {}).pop('id', None)
        elif target in record:
            record[target + '_id'] = record.pop(target)
        else:
            record[target + '_id'] = None

    def _flatten_list(self, record: Dict[str, Any], target: str):
        record[target] = [target_data.get("id") for target_data in record.get(target, [])]


class GitlabSubStream(GitlabStream):
    path_list = ["id"]

    def __init__(self, parent_stream: GitlabStream, parent_similar: bool = False, repository_part: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.parent_stream = parent_stream
        self.parent_similar = parent_similar
        self.repo_url = repository_part

    @property
    def path_template(self) -> str:
        template = [self.parent_stream.name] + ["{" + p + "}" for p in self.path_list]
        if self.repo_url:
            template.append("repository")
        template.append(casing.camel_to_snake(self.__class__.__name__))
        return "/".join(template)

    @property
    def name(self) -> str:
        if self.parent_similar:
            return f"{self.parent_stream.name[:-1]}_{super().name}"
        return super().name

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for slice in self.parent_stream.stream_slices(sync_mode=SyncMode.full_refresh):
            for record in self.parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice):
                yield {k: record[k] for k in self.path_list}

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return self.path_template.format(**{k: stream_slice[k] for k in self.path_list})


class Groups(GitlabStream):

    def __init__(self, group_ids: List, **kwargs):
        super().__init__(**kwargs)
        self.group_ids = group_ids

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"groups/{stream_slice['id']}"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for gid in self.group_ids:
            yield {"id": gid}

    def transform(self, record, stream_slice: Mapping[str, Any] = None, **kwargs):
        record["projects"] = [
            {
                "id": project["id"], "path_with_namespace": project["path_with_namespace"]
            } for project in record.pop("projects", [])
        ]
        return record


class Projects(GitlabStream):
    stream_base_params = {"statistics": 1}

    def __init__(self, project_ids: List = None, parent_stream: GitlabStream = None, **kwargs):
        super().__init__(**kwargs)
        self.project_ids = project_ids
        self.parent_stream = parent_stream

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"projects/{stream_slice['id']}"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        group_project_ids = set()
        for slice in self.parent_stream.stream_slices(sync_mode=SyncMode.full_refresh):
            for record in self.parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice):
                group_project_ids.update({i["path_with_namespace"] for i in record["projects"]})
            for pid in group_project_ids:
                if not self.project_ids or self.project_ids and pid in self.project_ids:
                    yield {"id": pid.replace("/", "%2F")}


class Milestones(GitlabSubStream):
    pass


class Members(GitlabSubStream):

    def transform(self, record, stream_slice: Mapping[str, Any] = None, **kwargs):
        record[f"{self.parent_stream.name[:-1]}_id"] = stream_slice["id"]
        return record


class Labels(GitlabSubStream):

    def transform(self, record, stream_slice: Mapping[str, Any] = None, **kwargs):
        record[f"{self.parent_stream.name[:-1]}_id"] = stream_slice["id"]
        return record


class Branches(GitlabSubStream):
    primary_key = ["project_id", "name"]
    flatten_id_keys = ["commit"]

    def transform(self, record, stream_slice: Mapping[str, Any] = None, **kwargs):
        super().transform(record, stream_slice, **kwargs)
        record[f"{self.parent_stream.name[:-1]}_id"] = stream_slice["id"]
        return record


class Commits(GitlabSubStream):
    primary_key = ["project_id", "id"]
    stream_base_params = {"with_stats": True}

    def transform(self, record, stream_slice: Mapping[str, Any] = None, **kwargs):
        record[f"{self.parent_stream.name[:-1]}_id"] = stream_slice["id"]
        return record


class Issues(GitlabSubStream):
    primary_key = ["project_id", "id"]
    stream_base_params = {"scope": "all"}
    flatten_id_keys = ["author", "assignee", "closed_by", "milestone"]
    flatten_list_keys = ["assignees"]


class MergeRequests(GitlabSubStream):
    primary_key = ["project_id", "id"]
    stream_base_params = {"scope": "all"}
    flatten_id_keys = ["author", "assignee", "closed_by", "milestone", "merged_by"]
    flatten_list_keys = ["assignees"]


class MergeRequestCommits(GitlabSubStream):
    primary_key = ["project_id", "merge_request_iid", "id"]
    path_list = ["project_id", "iid"]

    path_template = 'projects/{project_id}/merge_requests/{iid}'

    def transform(self, record, stream_slice: Mapping[str, Any] = None, **kwargs):
        record['project_id'] = stream_slice['project_id']
        record['merge_request_iid'] = stream_slice['iid']

        return record


class Releases(GitlabSubStream):
    primary_key = ["project_id", "name"]
    flatten_id_keys = ["author", "commit"]
    flatten_list_keys = ["milestones"]

    def transform(self, record, stream_slice: Mapping[str, Any] = None, **kwargs):
        super().transform(record, stream_slice, **kwargs)
        record['project_id'] = stream_slice["id"]

        return record


class Tags(GitlabSubStream):
    primary_key = ["project_id", "name"]
    flatten_id_keys = ["commit"]

    def transform(self, record, stream_slice: Mapping[str, Any] = None, **kwargs):
        super().transform(record, stream_slice, **kwargs)
        record["project_id"] = stream_slice["id"]

        return record


class Pipelines(GitlabSubStream):
    primary_key = ["project_id", "pipeline_id", "id"]


class PipelinesExtended(GitlabSubStream):
    primary_key = ["project_id", "id"]
    path_list = ["project_id", "id"]
    path_template = 'projects/{project_id}/pipelines/{id}'


class Jobs(GitlabSubStream):
    primary_key = ["project_id", "pipeline_id", "id"]
    flatten_id_keys = ["user", "pipeline", "runner", "commit"]
    path_list = ["project_id", "id"]
    path_template = 'projects/{project_id}/pipelines/{id}/jobs'

    def transform(self, record, stream_slice: Mapping[str, Any] = None, **kwargs):
        super().transform(record, stream_slice, **kwargs)
        record["project_id"] = stream_slice["project_id"]
        return record


class Users(GitlabSubStream):
    pass


# TODO: No permissions to check
class Epics(GitlabSubStream):
    primary_key = ["id", "iid"]
    flatten_id_keys = ["author"]


# TODO: No permissions to check
class EpicIssues(GitlabSubStream):
    primary_key = ["project_id", "epic_issue_id"]
    path_list = ["group_id", "id"]
    flatten_id_keys = ["milestone", "assignee", "author"]
    flatten_list_keys = ["assignees"]
    path_template = "groups/{group_id}/epics/{id}/issues"
