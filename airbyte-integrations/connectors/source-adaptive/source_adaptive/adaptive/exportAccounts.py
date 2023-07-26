from jinja2 import Template

from datetime import datetime
from typing import Generator

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    Type,
)
from source_adaptive.adaptive.base import Adaptive
from airbyte_cdk.sources import Source
from datetime import datetime


class AdaptiveExportAccounts(Adaptive):
    def construct_payload(self) -> Generator[str, None, None]:
        yield self.construct_payload_fast()

    def construct_payload_fast(self) -> str:
        """
        Generate the xml that is sent to the request using jinja templating
        """

        TEMPLATE = """<?xml version='1.0' encoding='UTF-8'?>
        <call method="{{method_obj["method"]}}" callerName="Airbyte - auto">
            <credentials login="{{username}}" password="{{password}}"/>
        </call>"""

        payload = Template(TEMPLATE).render(**self.config)
        return payload

    def generate_table_name(self):
        return "exportAccounts"

    def generate_table_schema(self):
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "code": {"type": "string"},
                "description": {"type": "string"},
                "timeStratum": {"type": "string"},
                "displayAs": {"type": "string"},
                "accountTypeCode": {"type": "string"},
                "decimalPrecision": {"type": "string"},
                "isAssumption": {"type": "string"},
                "suppressZeroes": {"type": "string"},
                "isDefaultRoot": {"type": "string"},
                "shortName": {"type": "string"},
                "exchangeRateType": {"type": "string"},
                "balanceType": {"type": "string"},
                "isLinked": {"type": "string"},
                "owningSheetId": {"type": "string"},
                "isSystem": {"type": "string"},
                "isIntercompany": {"type": "string"},
                "dataEntryType": {"type": "string"},
                "planBy": {"type": "string"},
                "actualsBy": {"type": "string"},
                "timeRollup": {"type": "string"},
                "timeWeightAcctId": {"type": "string"},
                "levelDimRollup": {"type": "string"},
                "levelDimWeightAcctId": {"type": "string"},
                "rollupText": {"type": "string"},
                "startExpanded": {"type": "string"},
                "hasSalaryDetail": {"type": "string"},
                "dataPrivacy": {"type": "string"},
                "isBreakbackEligible": {"type": "string"},
                "subType": {"type": "string"},
                "enableActuals": {"type": "string"},
                "isGroup": {"type": "string"},
                "hasFormula": {"type": "string"},
                "attributes": {"type": "string"},
                "parent_id": {"type": "string"},
                "parent_code": {"type": "string"},
                "parent_name": {"type": "string"},
            },
        }

        return json_schema

    def parse_attributes(self,d) -> str:
        if not d:
            return ""

        attribute_records = []

        attributes = d.get("attribute")
        if isinstance(attributes, list):
            for attribute in attributes:
                record = {}
                for k, v in attribute.items():
                    record[k.replace("@", "")] = v

                attribute_records.append(record)
        elif isinstance(attributes, dict):
            record = {}
            for k, v in attributes.items():
                record[k.replace("@", "")] = v
            attribute_records.append(record)

        return str(attribute_records)

    def parse_account_row(self, data_obj, parent_obj):

        data = {
            "id": data_obj.get("@id",""),
            "name": data_obj.get("@name",""),
            "code": data_obj.get("@code",""),
            "description": data_obj.get("@description",""),
            "timeStratum": data_obj.get("@timeStratum",""),
            "displayAs": data_obj.get("@displayAs",""),
            "accountTypeCode": data_obj.get("@accountTypeCode",""),
            "decimalPrecision": data_obj.get("@decimalPrecision",""),
            "isAssumption": data_obj.get("@isAssumption",""),
            "suppressZeroes": data_obj.get("@suppressZeroes",""),
            "isDefaultRoot": data_obj.get("@isDefaultRoot",""),
            "shortName": data_obj.get("@shortName",""),
            "exchangeRateType": data_obj.get("@exchangeRateType",""),
            "balanceType": data_obj.get("@balanceType",""),
            "isLinked": data_obj.get("@isLinked",""),
            "owningSheetId": data_obj.get("@owningSheetId",""),
            "isSystem": data_obj.get("@isSystem",""),
            "isIntercompany": data_obj.get("@isIntercompany",""),
            "dataEntryType": data_obj.get("@dataEntryType",""),
            "planBy": data_obj.get("@planBy",""),
            "actualsBy": data_obj.get("@actualsBy",""),
            "timeRollup": data_obj.get("@timeRollup",""),
            "timeWeightAcctId": data_obj.get("@timeWeightAcctId",""),
            "levelDimRollup": data_obj.get("@levelDimRollup",""),
            "levelDimWeightAcctId": data_obj.get("@levelDimWeightAcctId",""),
            "rollupText": data_obj.get("@rollupText",""),
            "startExpanded": data_obj.get("@startExpanded",""),
            "hasSalaryDetail": data_obj.get("@hasSalaryDetail",""),
            "dataPrivacy": data_obj.get("@dataPrivacy",""),
            "isBreakbackEligible": data_obj.get("@isBreakbackEligible",""),
            "subType": data_obj.get("@subType",""),
            "enableActuals": data_obj.get("@enableActuals",""),
            "isGroup": data_obj.get("@isGroup",""),
            "hasFormula": data_obj.get("@hasFormula",""),
            "attributes": self.parse_attributes(data_obj.get("attributes","")),
            "parent_id": parent_obj.get("parent_id",""),
            "parent_code": parent_obj.get("parent_code",""),
            "parent_name": parent_obj.get("parent_name",""),
        }
        # create a list of airbyte_messages

        parent_obj={
                "parent_id":data["id"],
                "parent_code":data["code"],
                "parent_name":data["name"],
                }

        yield AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(stream=self.generate_table_name(), data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
        )

        if "account" in data_obj:
            children = data_obj["account"]

            # check if children is provided as list or as single 
            if isinstance(children,list):
                for record_found in children:
                    yield from self.parse_account_row(data_obj=record_found,parent_obj=parent_obj)

            elif isinstance(children,dict):
                # this is single child
                yield from self.parse_account_row(data_obj=children,parent_obj=parent_obj)

    def generate_table_row(self) -> Generator[AirbyteMessage, None, None]:

        for response in self.perform_request():
            response_data = self.get_data_from_response(response)
            for row in response_data["accounts"]["account"]:
                yield from self.parse_account_row(data_obj=row,parent_obj={})
