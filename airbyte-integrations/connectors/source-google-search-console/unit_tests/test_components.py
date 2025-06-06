# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import pytest
from source_google_search_console.components import NestedSubstreamStateMigration


@pytest.mark.parametrize(
    "stream_state,expected_should_migrate,expected_migrated_state",
    [
        pytest.param(
            {
                "date": "2025-05-14",
                "https://evangelion.com": {"web": {"date": "2025-05-30"}, "news": {"date": "2025-05-23"}, "image": {"date": "2025-05-16"}},
                "https://nerv.gov": {"web": {"date": "2025-05-28"}, "news": {"date": "2025-05-21"}, "image": {"date": "2025-05-14"}},
            },
            True,
            {
                "use_global_cursor": False,
                "states": [
                    {"partition": {"search_type": "web", "site_url": "https://evangelion.com"}, "cursor": {"date": "2025-05-30"}},
                    {"partition": {"search_type": "news", "site_url": "https://evangelion.com"}, "cursor": {"date": "2025-05-23"}},
                    {"partition": {"search_type": "image", "site_url": "https://evangelion.com"}, "cursor": {"date": "2025-05-16"}},
                    {"partition": {"search_type": "web", "site_url": "https://nerv.gov"}, "cursor": {"date": "2025-05-28"}},
                    {"partition": {"search_type": "news", "site_url": "https://nerv.gov"}, "cursor": {"date": "2025-05-21"}},
                    {"partition": {"search_type": "image", "site_url": "https://nerv.gov"}, "cursor": {"date": "2025-05-14"}},
                ],
            },
            id="test_migrate_legacy_state_to_per_partition_state",
        ),
        pytest.param(
            {
                "use_global_cursor": False,
                "states": [
                    {"partition": {"search_type": "web", "site_url": "https://evangelion.com"}, "cursor": {"date": "2025-05-30"}},
                    {"partition": {"search_type": "news", "site_url": "https://evangelion.com"}, "cursor": {"date": "2025-05-23"}},
                    {"partition": {"search_type": "image", "site_url": "https://evangelion.com"}, "cursor": {"date": "2025-05-16"}},
                    {"partition": {"search_type": "web", "site_url": "https://nerv.gov"}, "cursor": {"date": "2025-05-28"}},
                    {"partition": {"search_type": "news", "site_url": "https://nerv.gov"}, "cursor": {"date": "2025-05-21"}},
                    {"partition": {"search_type": "image", "site_url": "https://nerv.gov"}, "cursor": {"date": "2025-05-14"}},
                ],
                "state": {"date": "2025-05-14"},
            },
            False,
            None,
            id="test_do_not_migrate_if_already_per_partition_state",
        ),
        pytest.param({}, False, None, id="test_do_not_migrate_empty_state"),
    ],
)
def test_nested_substream(stream_state, expected_should_migrate, expected_migrated_state):
    component = NestedSubstreamStateMigration()

    should_migrate = component.should_migrate(stream_state=stream_state)
    assert should_migrate == expected_should_migrate

    if should_migrate:
        migrated_state = component.migrate(stream_state=stream_state)
        assert migrated_state == expected_migrated_state
