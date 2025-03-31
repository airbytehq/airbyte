#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from conftest import BASE_CONFIG, GROUPS_LIST_URL, get_stream_by_name

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice


class TestGroupStreamsPartitionRouter:
    def test_groups_stream_slices_without_group_ids_in_config(self, requests_mock):
        requests_mock.get(url=GROUPS_LIST_URL, json=[{"id": "group_id_1"}, {"id": "group_id_2"}])
        groups_stream = get_stream_by_name("groups", BASE_CONFIG)
        assert list(groups_stream.stream_slices(sync_mode=SyncMode.full_refresh)) == [
            StreamSlice(partition={"id": "group_id_1"}, cursor_slice={}),
            StreamSlice(partition={"id": "group_id_2"}, cursor_slice={}),
        ]

    def test_groups_stream_slices_with_group_ids_in_config(self, requests_mock):
        groups_list = ["group_id_1", "group_id_2"]
        expected_stream_slices = []

        for group_id in groups_list:
            requests_mock.get(url=f"https://gitlab.com/api/v4/groups/{group_id}?per_page=50", json=[{"id": group_id}])
            requests_mock.get(
                url=f"https://gitlab.com/api/v4/groups/{group_id}/descendant_groups?per_page=50",
                json=[{"id": f"descendant_{group_id}"}],
            )
            expected_stream_slices.append(StreamSlice(partition={"id": group_id}, cursor_slice={}))
            expected_stream_slices.append(StreamSlice(partition={"id": f"descendant_{group_id}"}, cursor_slice={}))

        groups_stream = get_stream_by_name("groups", BASE_CONFIG | {"groups_list": groups_list})
        assert list(groups_stream.stream_slices(sync_mode=SyncMode.full_refresh)) == expected_stream_slices


class TestProjectStreamsPartitionRouter:
    projects_config = {"projects_list": ["group_id_1/project_id_1", "group_id_2/project_id_2"]}

    def test_projects_stream_slices_without_group_project_ids(self, requests_mock):
        requests_mock.get(url=GROUPS_LIST_URL, json=[])
        projects_stream = get_stream_by_name("projects", BASE_CONFIG | self.projects_config)
        assert list(projects_stream.stream_slices(sync_mode=SyncMode.full_refresh)) == [
            StreamSlice(partition={"id": "group_id_1%2Fproject_id_1"}, cursor_slice={}),
            StreamSlice(partition={"id": "group_id_2%2Fproject_id_2"}, cursor_slice={}),
        ]

    def test_projects_stream_slices_with_group_project_ids(self, requests_mock):
        groups_list = ["group_id_1", "group_id_2"]
        groups_list_response = []
        expected_stream_slices = []

        for group_id, project_id in zip(groups_list, self.projects_config["projects_list"]):
            groups_list_response.append({"id": group_id})
            requests_mock.get(
                url=f"https://gitlab.com/api/v4/groups/{group_id}?per_page=50",
                json=[{"id": group_id, "projects": [{"id": project_id, "path_with_namespace": project_id}]}],
            )
            expected_stream_slices.append(StreamSlice(partition={"id": project_id.replace("/", "%2F")}, cursor_slice={}))

        requests_mock.get(url=GROUPS_LIST_URL, json=groups_list_response)

        projects_stream = get_stream_by_name("projects", BASE_CONFIG | self.projects_config)
        assert list(projects_stream.stream_slices(sync_mode=SyncMode.full_refresh)) == expected_stream_slices

    def test_projects_stream_slices_with_group_project_ids_filtered_by_projects_list_config(self, requests_mock):
        group_id = "group_id_1"
        project_id = self.projects_config["projects_list"][0]
        unknown_project_id = "unknown_project_id"
        requests_mock.get(url=GROUPS_LIST_URL, json=[{"id": group_id}])
        requests_mock.get(
            url=f"https://gitlab.com/api/v4/groups/{group_id}?per_page=50",
            json=[
                {
                    "id": group_id,
                    "projects": [
                        {"id": project_id, "path_with_namespace": project_id},
                        {"id": unknown_project_id, "path_with_namespace": unknown_project_id},
                    ],
                },
            ],
        )

        projects_stream = get_stream_by_name("projects", BASE_CONFIG | self.projects_config)
        assert list(projects_stream.stream_slices(sync_mode=SyncMode.full_refresh)) == [
            StreamSlice(partition={"id": project_id.replace("/", "%2F")}, cursor_slice={})
        ]
