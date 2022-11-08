#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class GitlabStream(HttpStream, ABC):
    primary_key = "id"
    stream_base_params = {}
    flatten_id_keys = []
    flatten_list_keys = []
    page = 1
    per_page = 50

    def __init__(self, api_url: str, **kwargs):
        super().__init__(**kwargs)
        self.api_url = api_url

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"per_page": self.per_page}
        if next_page_token:
            params.update(next_page_token)
        params.update(self.stream_base_params)
        return params

    @property
    def url_base(self) -> str:
        return f"https://{self.api_url}/api/v4/"

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
            Exception(f"Unsupported type of response data for stream {self.name}")

    def transform(self, record: Dict[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs):
        for key in self.flatten_id_keys:
            self._flatten_id(record, key)

        for key in self.flatten_list_keys:
            self._flatten_list(record, key)

        return record

    def _flatten_id(self, record: Dict[str, Any], target: str):
        target_value = record.pop(target, None)
        record[target + "_id"] = target_value.get("id") if target_value else None

    def _flatten_list(self, record: Dict[str, Any], target: str):
        record[target] = [target_data.get("id") for target_data in record.get(target, [])]


class GitlabChildStream(GitlabStream):
    path_list = ["id"]
    flatten_parent_id = False

    def __init__(self, parent_stream: GitlabStream, repository_part: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.parent_stream = parent_stream
        self.repo_url = repository_part

    @property
    def path_template(self) -> str:
        template = [self.parent_stream.name] + ["{" + path_key + "}" for path_key in self.path_list]
        if self.repo_url:
            template.append("repository")
        return "/".join(template + [self.name])

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for slice in self.parent_stream.stream_slices(sync_mode=SyncMode.full_refresh):
            for record in self.parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice):
                yield {path_key: record[path_key] for path_key in self.path_list}

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return self.path_template.format(**{path_key: stream_slice[path_key] for path_key in self.path_list})

    def transform(self, record: Dict[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs):
        super().transform(record, stream_slice, **kwargs)
        if self.flatten_parent_id:
            record[f"{self.parent_stream.name[:-1]}_id"] = stream_slice["id"]
        return record


class IncrementalGitlabChildStream(GitlabChildStream):
    state_checkpoint_interval = 100
    cursor_field = "updated_at"
    filter_field = "updated_after"

    def __init__(self, start_date, **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        project_id = latest_record.get("project_id")
        latest_cursor_value = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(str(project_id))
        if current_state:
            current_state = current_state.get(self.cursor_field)
        current_state_value = current_state or latest_cursor_value
        max_value = max(pendulum.parse(current_state_value), pendulum.parse(latest_cursor_value))
        current_stream_state[str(project_id)] = {self.cursor_field: str(max_value)}
        return current_stream_state

    def request_params(self, stream_state=None, stream_slice: Mapping[str, Any] = None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state, stream_slice, **kwargs)

        start_point = self._start_date
        state_project_value = stream_state.get(str(stream_slice["id"]))
        if state_project_value:
            state_value = state_project_value.get(self.cursor_field)
            if state_value:
                start_point = max(start_point, state_value)
        params[self.filter_field] = start_point
        return params


class Groups(GitlabStream):
    use_cache = True

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
            {"id": project["id"], "path_with_namespace": project["path_with_namespace"]} for project in record.pop("projects", [])
        ]
        return record


class Projects(GitlabStream):
    stream_base_params = {"statistics": 1}
    use_cache = True

    def __init__(self, project_ids: List = None, **kwargs):
        super().__init__(**kwargs)
        self.project_ids = project_ids

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"projects/{stream_slice['id']}"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for pid in self.project_ids:
            yield {"id": pid.replace("/", "%2F")}


class GroupProjects(Projects):
    name = "projects"

    def __init__(self, parent_stream: GitlabStream = None, **kwargs):
        super().__init__(**kwargs)
        self.parent_stream = parent_stream

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        group_project_ids = set()
        for slice in self.parent_stream.stream_slices(sync_mode=SyncMode.full_refresh):
            for record in self.parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice):
                group_project_ids.update({i["path_with_namespace"] for i in record["projects"]})
            for pid in group_project_ids:
                if not self.project_ids or self.project_ids and pid in self.project_ids:
                    yield {"id": pid.replace("/", "%2F")}


class GroupMilestones(GitlabChildStream):
    path_template = "groups/{id}/milestones"


class ProjectMilestones(GitlabChildStream):
    path_template = "projects/{id}/milestones"


class GroupMembers(GitlabChildStream):
    path_template = "groups/{id}/members"
    flatten_parent_id = True


class ProjectMembers(GitlabChildStream):
    path_template = "projects/{id}/members"
    flatten_parent_id = True


class GroupLabels(GitlabChildStream):
    path_template = "groups/{id}/labels"
    flatten_parent_id = True


class ProjectLabels(GitlabChildStream):
    path_template = "projects/{id}/labels"
    flatten_parent_id = True


class Branches(GitlabChildStream):
    primary_key = "name"
    flatten_id_keys = ["commit"]
    flatten_parent_id = True


class Commits(IncrementalGitlabChildStream):
    cursor_field = "created_at"
    filter_field = "since"
    flatten_parent_id = True
    stream_base_params = {"with_stats": True}


class Issues(IncrementalGitlabChildStream):
    stream_base_params = {"scope": "all"}
    flatten_id_keys = ["author", "assignee", "closed_by", "milestone"]
    flatten_list_keys = ["assignees"]


class MergeRequests(IncrementalGitlabChildStream):
    stream_base_params = {"scope": "all"}
    flatten_id_keys = ["author", "assignee", "closed_by", "milestone", "merged_by"]
    flatten_list_keys = ["assignees"]


class MergeRequestCommits(GitlabChildStream):
    path_list = ["project_id", "iid"]
    path_template = "projects/{project_id}/merge_requests/{iid}"

    def transform(self, record, stream_slice: Mapping[str, Any] = None, **kwargs):
        super().transform(record, stream_slice, **kwargs)
        record["project_id"] = stream_slice["project_id"]
        record["merge_request_iid"] = stream_slice["iid"]

        return record


class Releases(GitlabChildStream):
    primary_key = "name"
    flatten_id_keys = ["author", "commit"]
    flatten_list_keys = ["milestones"]

    def transform(self, record, stream_slice: Mapping[str, Any] = None, **kwargs):
        super().transform(record, stream_slice, **kwargs)
        record["project_id"] = stream_slice["id"]

        return record


class Tags(GitlabChildStream):
    primary_key = "name"
    flatten_id_keys = ["commit"]

    def transform(self, record, stream_slice: Mapping[str, Any] = None, **kwargs):
        super().transform(record, stream_slice, **kwargs)
        record["project_id"] = stream_slice["id"]

        return record


class Pipelines(IncrementalGitlabChildStream):
    pass


class PipelinesExtended(GitlabChildStream):
    path_list = ["project_id", "id"]
    path_template = "projects/{project_id}/pipelines/{id}"


class Jobs(GitlabChildStream):
    flatten_id_keys = ["user", "pipeline", "runner", "commit"]
    path_list = ["project_id", "id"]
    path_template = "projects/{project_id}/pipelines/{id}/jobs"

    def transform(self, record, stream_slice: Mapping[str, Any] = None, **kwargs):
        super().transform(record, stream_slice, **kwargs)
        record["project_id"] = stream_slice["project_id"]
        return record


class GroupIssueBoards(GitlabChildStream):
    path_template = "groups/{id}/boards"
    flatten_parent_id = True


class Users(GitlabChildStream):
    pass


# TODO: We need to upgrade the plan for these feature (epics) to be available
class Epics(GitlabChildStream):
    primary_key = "iid"
    flatten_id_keys = ["author"]


# TODO: We need to upgrade the plan for these feature (epics) to be available
class EpicIssues(GitlabChildStream):
    primary_key = "epic_issue_id"
    path_list = ["group_id", "id"]
    flatten_id_keys = ["milestone", "assignee", "author"]
    flatten_list_keys = ["assignees"]
    path_template = "groups/{group_id}/epics/{id}/issues"
