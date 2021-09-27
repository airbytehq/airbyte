#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from typing import Dict

from airbyte_protocol import AirbyteConnectionStatus, Status, SyncMode
from base_python import AirbyteLogger
from base_singer import BaseSingerSource, SyncModeInfo


class SourceMarketoSinger(BaseSingerSource):
    tap_cmd = "tap-marketo"
    tap_name = "Marketo API"
    api_error = Exception

    def transform_config(self, raw_config):
        return {
            "endpoint": raw_config["endpoint_url"],
            "identity": raw_config["identity_url"],
            "client_id": raw_config["client_id"],
            "client_secret": raw_config["client_secret"],
            "start_date": raw_config["start_date"],
        }

    def try_connect(self, logger: AirbyteLogger, config_path: str):
        self.discover(logger, config_path)

    def check_config(self, logger: AirbyteLogger, config_path: str, config: json) -> AirbyteConnectionStatus:
        try:
            self.try_connect(logger, config_path)
        except self.api_error as err:
            logger.error(f"Exception while connecting to {self.tap_name}: {err}")
            # this should be in UI
            error_msg = f"Unable to connect to {self.tap_name} with the provided credentials."
            return AirbyteConnectionStatus(status=Status.FAILED, message=error_msg)
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def get_sync_mode_overrides(self) -> Dict[str, SyncModeInfo]:
        incremental_streams = [
            "leads",
            "activities_visit_webpage",
            "activities_fill_out_form",
            "activities_click_link",
            "activities_send_email",
            "activities_email_delivered",
            "activities_email_bounced",
            "activities_unsubscribe_email",
            "activities_open_email",
            "activities_click_email",
            "activities_new_lead",
            "activities_change_data_value",
            "activities_change_score",
            "activities_add_to_list",
            "activities_remove_from_list",
            "activities_email_bounced_soft",
            "activities_merge_leads",
            "activities_add_to_opportunity",
            "activities_remove_from_opportunity",
            "activities_update_opportunity",
            "activities_delete_lead",
            "activities_send_alert",
            "activities_send_sales_email",
            "activities_open_sales_email",
            "activities_click_sales_email",
            "activities_receive_sales_email",
            "activities_request_campaign",
            "activities_sales_email_bounced",
            "activities_change_lead_partition",
            "activities_change_revenue_stage",
            "activities_change_revenue_stage_manually",
            "activities_change_status_in_progression",
            "activities_change_segment",
            "activities_call_webhook",
            "activities_sent_forward_to_friend_email",
            "activities_received_forward_to_friend_email",
            "activities_add_to_nurture",
            "activities_change_nurture_track",
            "activities_change_nurture_cadence",
            "activities_change_program_member_data",
            "activities_push_lead_to_marketo",
            "activities_share_content",
            "campaigns",
            "lists",
            "programs",
        ]

        return {s: SyncModeInfo([SyncMode.incremental], True, []) for s in incremental_streams}

    def read_cmd(self, logger: AirbyteLogger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        state_opt = f"--state {state_path}" if state_path else ""
        return f"{self.tap_cmd} --config {config_path} --properties {catalog_path} {state_opt}"
