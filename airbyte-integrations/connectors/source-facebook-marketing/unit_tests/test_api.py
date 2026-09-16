#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from datetime import timedelta

import pytest
import source_facebook_marketing
from facebook_business import FacebookAdsApi, FacebookSession
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.exceptions import FacebookRequestError


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
                timedelta(minutes=5),
                timedelta(minutes=1),
                96,
                timedelta(minutes=6),
                timedelta(minutes=6),
            ),
            (
                95,
                timedelta(minutes=5),
                timedelta(minutes=2),
                96,
                timedelta(minutes=1),
                timedelta(minutes=5),
            ),
            (
                95,
                timedelta(minutes=5),
                timedelta(minutes=1),
                93,
                timedelta(minutes=4),
                timedelta(minutes=4),
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
                timedelta(minutes=1),  # min_pause_interval
                [
                    (5, timedelta(minutes=6)),
                    (7, timedelta(minutes=5)),
                ],  # usages_pause_intervals
                (7, timedelta(minutes=6)),  # expected_output
            ),
            (
                timedelta(minutes=10),  # min_pause_interval
                [
                    (5, timedelta(minutes=6)),
                    (7, timedelta(minutes=5)),
                ],  # usages_pause_intervals
                (7, timedelta(minutes=10)),  # expected_output
            ),
            (
                timedelta(minutes=10),  # min_pause_interval
                [  # usages_pause_intervals
                    (9, timedelta(minutes=6)),
                ],
                (9, timedelta(minutes=10)),  # expected_output
            ),
            (
                timedelta(minutes=10),  # min_pause_interval
                [  # usages_pause_intervals
                    (-1, timedelta(minutes=1)),
                    (-2, timedelta(minutes=10)),
                    (-3, timedelta(minutes=100)),
                ],
                (0, timedelta(minutes=100)),  # expected_output
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
                f"Facebook API Utilization is too high ({usage})%, pausing for {fb_api._compute_pause_interval.return_value}"
            )

    @pytest.mark.parametrize(
        "headers,expected_usage",
        [
            # String-typed values from Facebook API JSON (the bug scenario)
            (
                {"x-ad-account-usage": '{"acc_id_util_pct": "75.5"}'},
                75.5,
            ),
            # Numeric values (normal case, should still work)
            (
                {"x-ad-account-usage": '{"acc_id_util_pct": 42}'},
                42,
            ),
            # String-typed values in x-app-usage header
            (
                {"x-app-usage": '{"call_count": "10", "total_time": "20.5", "total_cputime": "5"}'},
                20.5,
            ),
            # String-typed values in x-business-use-case-usage header
            (
                {
                    "x-business-use-case-usage": '{"biz_123": [{"call_count": "30", "total_cputime": "60", "total_time": "45", "estimated_time_to_regain_access": 0}]}'
                },
                60,
            ),
            # Missing keys should default to 0
            (
                {"x-ad-account-usage": "{}"},
                0,
            ),
            # No rate-limit headers at all
            (
                {},
                0,
            ),
        ],
    )
    def test_parse_call_rate_header_handles_string_values(self, fb_api, headers, expected_usage):
        usage, _ = fb_api._parse_call_rate_header(headers)
        assert usage == expected_usage
        assert isinstance(usage, (int, float))

    def test_update_insights_throttle_limit_casts_string_values(self, fb_api, mocker):
        mock_response = mocker.Mock()
        mock_response.headers.return_value = {"x-fb-ads-insights-throttle": '{"app_id_util_pct": "55.5", "acc_id_util_pct": "30"}'}
        fb_api._update_insights_throttle_limit(mock_response)
        assert fb_api._ads_insights_throttle.per_application == 55.5
        assert fb_api._ads_insights_throttle.per_account == 30.0
        assert isinstance(fb_api._ads_insights_throttle.per_application, float)
        assert isinstance(fb_api._ads_insights_throttle.per_account, float)

    @staticmethod
    def _make_error(code, subcode=None, headers=None, is_transient=False):
        error = {"message": "Ad Account Has Too Many API Calls", "code": code, "is_transient": is_transient}
        if subcode is not None:
            error["error_subcode"] = subcode
        return FacebookRequestError(
            message="Call was not successful",
            request_context={},
            http_status=400,
            http_headers=headers or {},
            body=json.dumps({"error": error}),
        )

    @pytest.mark.parametrize(
        "code,subcode,expected",
        [
            (17, 2446079, True),  # the observed "Ad Account Has Too Many API Calls" block
            (17, 1234567, False),  # same code, an unobserved subcode
            (17, None, False),
            (4, None, False),  # app-level throttling isn't wired up yet
            (100, 12345, False),
        ],
    )
    def test__is_quota_block_error(self, fb_api, code, subcode, expected):
        assert fb_api._is_quota_block_error(self._make_error(code, subcode)) == expected

    def test__handle_quota_block_error_uses_header_derived_wait(self, mocker, fb_api):
        headers = {
            "x-business-use-case-usage": json.dumps(
                {"act_123": [{"call_count": 100, "total_cputime": 100, "total_time": 100, "estimated_time_to_regain_access": 7}]}
            )
        }
        exc = self._make_error(17, 2446079, headers=headers)
        mocker.patch.object(source_facebook_marketing.api, "sleep")
        mocker.patch.object(source_facebook_marketing.api, "logger")

        fb_api._handle_quota_block_error(exc)

        source_facebook_marketing.api.sleep.assert_called_once_with(timedelta(minutes=7).total_seconds())
        warning_message = source_facebook_marketing.api.logger.warning.call_args[0][0]
        assert "code=17" in warning_message and "subcode=2446079" in warning_message

    def test__handle_quota_block_error_caps_wait_at_max_pause_interval(self, mocker, fb_api):
        headers = {
            "x-business-use-case-usage": json.dumps(
                {"act_123": [{"call_count": 100, "total_cputime": 100, "total_time": 100, "estimated_time_to_regain_access": 60}]}
            )
        }
        exc = self._make_error(17, 2446079, headers=headers)
        mocker.patch.object(source_facebook_marketing.api, "sleep")

        fb_api._handle_quota_block_error(exc)

        source_facebook_marketing.api.sleep.assert_called_once_with(fb_api.MAX_PAUSE_INTERVAL.total_seconds())

    def test__handle_quota_block_error_falls_back_to_default_when_field_missing(self, mocker, fb_api):
        exc = self._make_error(17, 2446079, headers={})
        mocker.patch.object(source_facebook_marketing.api, "sleep")

        fb_api._handle_quota_block_error(exc)

        source_facebook_marketing.api.sleep.assert_called_once_with(fb_api.MAX_PAUSE_INTERVAL.total_seconds())

    def test__handle_failed_call_rate_limit_applies_generic_pause(self, mocker, fb_api):
        headers = {"x-ad-account-usage": json.dumps({"acc_id_util_pct": 96})}
        exc = self._make_error(100, 12345, headers=headers)
        mocker.patch.object(source_facebook_marketing.api, "sleep")
        mocker.patch.object(source_facebook_marketing.api, "logger")

        fb_api._handle_failed_call_rate_limit(exc)

        source_facebook_marketing.api.sleep.assert_called_once()
        source_facebook_marketing.api.logger.warning.assert_called_once()

    def test__handle_failed_call_rate_limit_no_pause_when_usage_low(self, mocker, fb_api):
        headers = {"x-ad-account-usage": json.dumps({"acc_id_util_pct": 10})}
        exc = self._make_error(100, 12345, headers=headers)
        mocker.patch.object(source_facebook_marketing.api, "sleep")

        fb_api._handle_failed_call_rate_limit(exc)

        source_facebook_marketing.api.sleep.assert_not_called()

    def test_call_retries_quota_block_without_raising(self, mocker, fb_api):
        """The error path must read the response headers and derive the wait from
        `estimated_time_to_regain_access`, retrying the call itself rather than propagating --
        this is what keeps the retry from being counted against @backoff_policy's max_tries."""
        headers = {
            "x-business-use-case-usage": json.dumps(
                {"act_123": [{"call_count": 100, "total_cputime": 100, "total_time": 100, "estimated_time_to_regain_access": 2}]}
            )
        }
        quota_error = self._make_error(17, 2446079, headers=headers)
        success_response = mocker.Mock()
        success_response.headers.return_value = {}

        mock_super_call = mocker.patch.object(FacebookAdsApi, "call", side_effect=[quota_error, success_response])
        mocker.patch.object(source_facebook_marketing.api, "sleep")

        response = source_facebook_marketing.api.MyFacebookAdsApi.call.__wrapped__(
            fb_api, method="GET", path=("act_123", "ads"), params={}
        )

        assert response is success_response
        assert mock_super_call.call_count == 2
        source_facebook_marketing.api.sleep.assert_called_once_with(timedelta(minutes=2).total_seconds())

    def test_call_gives_up_on_quota_block_after_max_wait(self, mocker, fb_api):
        """A quota block that never clears must not loop forever: once cumulative quota-wait time
        reaches MAX_QUOTA_BLOCK_WAIT, `call()` falls through to the same handling (and re-raise)
        as any other failed call, instead of retrying indefinitely."""
        quota_error = self._make_error(17, 2446079, headers={})

        mocker.patch.object(fb_api, "MAX_QUOTA_BLOCK_WAIT", timedelta(minutes=5))
        mock_handle_quota_block = mocker.patch.object(fb_api, "_handle_quota_block_error", return_value=timedelta(minutes=6))
        mock_handle_failed = mocker.patch.object(fb_api, "_handle_failed_call_rate_limit")
        mock_super_call = mocker.patch.object(FacebookAdsApi, "call", side_effect=quota_error)

        with pytest.raises(FacebookRequestError):
            source_facebook_marketing.api.MyFacebookAdsApi.call.__wrapped__(fb_api, method="GET", path=("act_123", "ads"), params={})

        # 1st failure: 0 min elapsed < 5 min cap -> retries, accrues 6 min.
        # 2nd failure: 6 min elapsed >= 5 min cap -> gives up instead of retrying again.
        assert mock_super_call.call_count == 2
        assert mock_handle_quota_block.call_count == 1
        mock_handle_failed.assert_called_once_with(quota_error)

    def test_call_reraises_non_quota_error_unchanged(self, mocker, fb_api):
        """A non-quota FacebookRequestError must still propagate out of `call()` so
        @backoff_policy's original expo ladder (unchanged) is the one that retries it."""
        headers = {"x-ad-account-usage": json.dumps({"acc_id_util_pct": 10})}
        other_error = self._make_error(100, 12345, headers=headers)

        mocker.patch.object(FacebookAdsApi, "call", side_effect=other_error)
        mock_handle_failed = mocker.patch.object(fb_api, "_handle_failed_call_rate_limit")

        with pytest.raises(FacebookRequestError):
            source_facebook_marketing.api.MyFacebookAdsApi.call.__wrapped__(fb_api, method="GET", path=("act_123", "ads"), params={})

        mock_handle_failed.assert_called_once_with(other_error)

    def test_find_account(self, api, account_id, requests_mock):
        requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/",
            [{"json": {"id": "act_test"}}],
        )
        account = api.get_account(account_id)
        assert isinstance(account, AdAccount)
        assert account.get_id() == "act_test"
