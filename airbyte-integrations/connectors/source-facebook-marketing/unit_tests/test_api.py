#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
import source_facebook_marketing
from facebook_business import FacebookAdsApi, FacebookSession
from facebook_business.adobjects.adaccount import AdAccount


FB_API_VERSION = FacebookAdsApi.API_VERSION


class TestMyFacebookAdsApi:
    @pytest.fixture
    def fb_api(self):
        return source_facebook_marketing.api.MyFacebookAdsApi.init(access_token="foo", crash_log=False)

    @pytest.mark.parametrize(
        "max_rate,max_pause_interval,min_pause_interval,usage,pause_interval,expected_pause_interval",
        [
            (
                95,
                pendulum.duration(minutes=5),
                pendulum.duration(minutes=1),
                96,
                pendulum.duration(minutes=6),
                pendulum.duration(minutes=6),
            ),
            (
                95,
                pendulum.duration(minutes=5),
                pendulum.duration(minutes=2),
                96,
                pendulum.duration(minutes=1),
                pendulum.duration(minutes=5),
            ),
            (
                95,
                pendulum.duration(minutes=5),
                pendulum.duration(minutes=1),
                93,
                pendulum.duration(minutes=4),
                pendulum.duration(minutes=4),
            ),
        ],
    )
    def test__compute_pause_interval(
        self,
        mocker,
        fb_api,
        max_rate,
        max_pause_interval,
        min_pause_interval,
        usage,
        pause_interval,
        expected_pause_interval,
    ):
        mocker.patch.object(fb_api, "MAX_RATE", max_rate)
        mocker.patch.object(fb_api, "MAX_PAUSE_INTERVAL", max_pause_interval)
        mocker.patch.object(fb_api, "MIN_PAUSE_INTERVAL", min_pause_interval)
        computed_pause_interval = fb_api._compute_pause_interval(usage, pause_interval)
        assert computed_pause_interval == expected_pause_interval

    @pytest.mark.parametrize(
        "min_pause_interval,usages_pause_intervals,expected_output",
        [
            (
                pendulum.duration(minutes=1),  # min_pause_interval
                [
                    (5, pendulum.duration(minutes=6)),
                    (7, pendulum.duration(minutes=5)),
                ],  # usages_pause_intervals
                (7, pendulum.duration(minutes=6)),  # expected_output
            ),
            (
                pendulum.duration(minutes=10),  # min_pause_interval
                [
                    (5, pendulum.duration(minutes=6)),
                    (7, pendulum.duration(minutes=5)),
                ],  # usages_pause_intervals
                (7, pendulum.duration(minutes=10)),  # expected_output
            ),
            (
                pendulum.duration(minutes=10),  # min_pause_interval
                [  # usages_pause_intervals
                    (9, pendulum.duration(minutes=6)),
                ],
                (9, pendulum.duration(minutes=10)),  # expected_output
            ),
            (
                pendulum.duration(minutes=10),  # min_pause_interval
                [  # usages_pause_intervals
                    (-1, pendulum.duration(minutes=1)),
                    (-2, pendulum.duration(minutes=10)),
                    (-3, pendulum.duration(minutes=100)),
                ],
                (0, pendulum.duration(minutes=100)),  # expected_output
            ),
        ],
    )
    def test__get_max_usage_pause_interval_from_batch(
        self,
        mocker,
        fb_api,
        min_pause_interval,
        usages_pause_intervals,
        expected_output,
    ):
        records = [
            {
                "headers": [
                    {"name": "USAGE", "value": usage},
                    {"name": "PAUSE_INTERVAL", "value": pause_interval},
                ]
            }
            for usage, pause_interval in usages_pause_intervals
        ]

        mock_parse_call_rate_header = mocker.Mock(side_effect=usages_pause_intervals)
        mocker.patch.object(fb_api, "_parse_call_rate_header", mock_parse_call_rate_header)
        mocker.patch.object(fb_api, "MIN_PAUSE_INTERVAL", min_pause_interval)

        output = fb_api._get_max_usage_pause_interval_from_batch(records)
        fb_api._parse_call_rate_header.assert_called_with(
            {
                "usage": usages_pause_intervals[-1][0],
                "pause_interval": usages_pause_intervals[-1][1],
            }
        )
        assert output == expected_output

    @pytest.mark.parametrize(
        "params,min_rate,usage,expect_sleep",
        [
            (["batch"], 0, 1, True),
            (["batch"], 0, 0, True),
            (["batch"], 2, 1, False),
            (["not_batch"], 0, 1, True),
            (["not_batch"], 0, 0, True),
            (["not_batch"], 2, 1, False),
        ],
    )
    def test__handle_call_rate_limit(self, mocker, fb_api, params, min_rate, usage, expect_sleep):
        pause_interval = 1
        mock_response = mocker.Mock()

        mocker.patch.object(fb_api, "MIN_RATE", min_rate)
        mocker.patch.object(
            fb_api,
            "_get_max_usage_pause_interval_from_batch",
            mocker.Mock(return_value=(usage, pause_interval)),
        )
        mocker.patch.object(
            fb_api,
            "_parse_call_rate_header",
            mocker.Mock(return_value=(usage, pause_interval)),
        )
        mocker.patch.object(fb_api, "_compute_pause_interval")
        mocker.patch.object(source_facebook_marketing.api, "logger")
        mocker.patch.object(source_facebook_marketing.api, "sleep")
        assert fb_api._handle_call_rate_limit(mock_response, params) is None
        if "batch" in params:
            fb_api._get_max_usage_pause_interval_from_batch.assert_called_with(mock_response.json.return_value)
        else:
            fb_api._parse_call_rate_header.assert_called_with(mock_response.headers.return_value)
        if expect_sleep:
            fb_api._compute_pause_interval.assert_called_with(usage=usage, pause_interval=pause_interval)
            source_facebook_marketing.api.sleep.assert_called_with(fb_api._compute_pause_interval.return_value.total_seconds())
            source_facebook_marketing.api.logger.warning.assert_called_with(
                f"Utilization is too high ({usage})%, pausing for {fb_api._compute_pause_interval.return_value}"
            )

    def test_find_account(self, api, account_id, requests_mock):
        requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/",
            [{"json": {"id": "act_test"}}],
        )
        account = api.get_account(account_id)
        assert isinstance(account, AdAccount)
        assert account.get_id() == "act_test"
