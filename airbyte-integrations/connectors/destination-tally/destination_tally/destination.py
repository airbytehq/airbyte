#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type

from .utils import *


class DestinationTally(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        """
        :param config: dict of JSON configuration matching the configuration declared in spec.json
        :param configured_catalog: The Configured Catalog describing the schema of the data being received and how it should be persisted in the
                                    destination
        :param input_messages: The stream of input messages received from the source

        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """
        logger = AirbyteLogger()
        for airbyte_message in input_messages:
            if airbyte_message.type == Type.RECORD:
                if "ledger" in airbyte_message.record.stream:
                    ledger_url = "https://api.excel2tally.in/api/User/LedgerMaster"
                    insert_ledger_master_to_tally(
                        config=config, data=airbyte_message.record.data, ledger_master_template_url=ledger_url, logger=logger
                    )
                elif "item" in airbyte_message.record.stream:
                    item_url = "https://api.excel2tally.in/api/User/ItemMaster"
                    insert_item_master_to_tally(
                        config=config, data=airbyte_message.record.data, item_master_template_url=item_url, logger=logger
                    )
                elif "payment" in airbyte_message.record.stream:
                    payment_voucher_url = "https://api.excel2tally.in/api/User/PaymentVoucher"
                    insert_payment_voucher_to_tally(
                        config=config, data=airbyte_message.record.data, payment_voucher_template_url=payment_voucher_url, logger=logger
                    )
            elif airbyte_message.type == Type.STATE:
                yield airbyte_message

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            if ("auth_key" not in config) or (config["auth_key"] == ""):
                logger.error("Please provide api auth key")
                return
            if ("company_name" not in config) or (config["company_name"] == ""):
                logger.error("Please provide company name.")
                return
            if ("version" not in config) or (config["version"] == ""):
                logger.error("Please provide version of tally prime software.")
                return
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
