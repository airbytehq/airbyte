#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from pipelines import bases
from pipelines.contexts import ConnectorContext

pytestmark = [
    pytest.mark.anyio,
]


class TestConnectorContext:
    @pytest.fixture
    def connector(self):
        return bases.ConnectorWithModifiedFiles("source-openweather", frozenset())

    @pytest.fixture
    def context(self, dagger_client, connector):
        context = ConnectorContext(
            pipeline_name="test",
            connector=connector,
            is_local=True,
            git_branch="test",
            git_revision="123",
            report_output_prefix="test",
        )
        context.dagger_client = dagger_client
        return context

    @pytest.mark.parametrize(
        ("include, exclude"),
        [
            (None, None),
            (["metadata.yaml"], None),
            (None, ["metadata.yaml"]),
            (["metadata.yaml"], ["metadata.yaml"]),
        ],
    )
    async def test_get_connector_dir(self, context, tmpdir, include, exclude):
        local_connector_tmp_dir = tmpdir / "local_connector"
        local_connector_tmp_dir.mkdir()

        if exclude and include:
            with pytest.raises(ValueError):
                await (await context.get_connector_dir(include=include, exclude=exclude)).export(str(tmpdir / "local_connector"))
        else:
            await (await context.get_connector_dir(include=include, exclude=exclude)).export(str(tmpdir / "local_connector"))
            if include is None and exclude is None:
                assert local_connector_tmp_dir.join("metadata.yaml").isfile()
                assert not local_connector_tmp_dir.join("acceptance_tests_logs").exists()
                assert not local_connector_tmp_dir.join("airbyte_ci_logs").exists()

            if exclude:
                for item in exclude:
                    assert not local_connector_tmp_dir.join(item).exists()
            if include:
                for item in include:
                    assert local_connector_tmp_dir.join(item).exists()
                assert len(include) == len(local_connector_tmp_dir.listdir())
