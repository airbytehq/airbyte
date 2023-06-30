from jinja2 import Template

from datetime import datetime
from typing import Generator, List

from source_adaptive.adaptive.base import Adaptive
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    Type,
)
from datetime import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AdaptiveExportData(Adaptive):
    def _generate_mapping_order_for_row(self) -> dict:
        """
        Since data is provided as csv and we read each record as list,
        it is helpful to create a mapping that maps where in the list
        is the respecitve column.
        """

        # first three columns are static and they are always retrieved
        mapping_order = {"account_name": 0, "account_code": 1, "level_code": 2, "level_name": 3}

        # now create a column for each dimensions that is requested with the order respected
        n_elems = len(mapping_order)
        dimensions = self.config["method_obj"]["dimensions"]
        # generate one additional column that will hold the code value of each dimension
        new_dimensions = [s for item in dimensions for s in [f"{item}_code", item]]
        mapping_order.update({d.replace(" ", "_").lower(): n + n_elems for n, d in enumerate(new_dimensions)})

        # the final column in row is attributed to the amount
        n_elems = len(mapping_order)
        mapping_order.update({"amount": n_elems})

        return mapping_order

    def _get_months_of_interest(self) -> List[str]:
        """
        Returns a list of all the months between start_month and end_month inclusive.
        """

        date_fmt = "%m/%Y"

        # Convert the start_month and end_month strings to datetime objects
        start_dt = datetime.strptime(self.config["method_obj"]["date_start"], date_fmt)
        end_dt = datetime.strptime(self.config["method_obj"]["date_end"], date_fmt)

        # Initialize an empty list to store the result
        months = []

        # Loop through each month between start_dt and end_dt using relativedelta
        while start_dt <= end_dt:
            months.append(start_dt.strftime(date_fmt))
            start_dt += relativedelta(months=1)
        return months

    def construct_payload(self) -> Generator[str, None, None]:
        """
        Generate the xml that is sent to the request using jinja templating
        """

        for date_selected in self._get_months_of_interest():
            for account_selected in self.config["method_obj"]["accounts"]:
                self.logger.info(f"Progress: date_selected:{date_selected} account_selected:{account_selected}")

                TEMPLATE = """<?xml version='1.0' encoding='UTF-8'?>
                <call method="{{method_obj["method"]}}" callerName="Airbyte - auto">
                    <credentials login="{{username}}" password="{{password}}"/>
                    <version name="{{method_obj["version"]}}" isDefault="false"/>
                    <format useInternalCodes="true" includeCodes="true" includeNames="true" displayNameEnabled="true"/>
                    <filters>
                        <accounts>
                            <account code="{{account_selected}}" isAssumption="false" includeDescendants="true"/>
                        </accounts>
                        <timeSpan start="{{date_selected}}" end="{{date_selected}}"/>
                    </filters>
                    <dimensions>
                        {% for dim in method_obj["dimensions"] -%}
                        <dimension name="{{dim}}"/>
                        {% endfor -%}
                    </dimensions>
                    <rules includeZeroRows="false" includeRollupAccounts="true" timeRollups="false">
                        <currency override="USD"/>
                    </rules>
                </call>"""

                config_with_added_properties = self.config
                config_with_added_properties.update({"date_selected": date_selected})
                config_with_added_properties.update({"account_selected": account_selected})

                payload = Template(TEMPLATE).render(**config_with_added_properties)
                yield payload

    def construct_payload_fast(self) -> str:

        """
        Generate the xml that is sent to the request using jinja templating
        """

        TEMPLATE = """<?xml version='1.0' encoding='UTF-8'?>
        <call method="{{method_obj["method"]}}" callerName="Airbyte - auto">
            <credentials login="{{username}}" password="{{password}}"/>
            <version name="{{method_obj["version"]}}" isDefault="false"/>
            <format useInternalCodes="true" includeCodes="true" includeNames="true" displayNameEnabled="true"/>
            <filters>
                <accounts>
                    <account code="{{method_obj["accounts"][0]}}" isAssumption="false" includeDescendants="true"/>
                </accounts>
                <timeSpan start="{{method_obj["date_start"]}}" end="{{method_obj["date_start"]}}"/>
            </filters>
            <dimensions>
                {% for dim in method_obj["dimensions"] -%}
                <dimension name="{{dim}}"/>
                {% endfor -%}
            </dimensions>
            <rules includeZeroRows="false" includeRollupAccounts="true" timeRollups="false">
                <currency override="USD"/>
            </rules>
        </call>"""

        payload = Template(TEMPLATE).render(**self.config)
        return payload

    def generate_table_name(self) -> str:
        return "exportData" + "_" + self.config["method_obj"]["version"]

    def generate_table_schema(self) -> dict:
        # form initial json_schema
        json_schema = {  # Example
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "account_name": {"type": "string"},
                "account_code": {"type": "string"},
                "level_code": {"type": "string"},
                "level_name": {"type": "string"},
            },
        }
        # add dimensions as string types
        dimensions = self.config["method_obj"]["dimensions"]
        # generate one additional column that will hold the code value of each dimension
        new_dimensions = [s for item in dimensions for s in [f"{item}_code", item]]
        json_schema["properties"].update({d.replace(" ", "_").lower(): {"type": "string"} for d in new_dimensions})

        # add an additional columns to keep the date, and the amount
        json_schema["properties"].update({"date": {"type": "string"}})
        json_schema["properties"].update({"amount": {"type": "string"}})
        json_schema["properties"].update({"version": {"type": "string"}})
        return json_schema

    def generate_table_row(self) -> Generator[AirbyteMessage, None, None]:

        # make the request and keep the response
        for response in self.perform_request():
            if response is None:
                raise ValueError

            # get the mapping dor each row in csv
            mapping_order = self._generate_mapping_order_for_row()

            # get the date_selected as it will be saved for each row
            date_selected = str(self.get_csv_columns_from_response(response)[-1])

            version = self.config["method_obj"]["version"]

            # generate a record for each row that is read
            for row in self.get_csv_data_from_response(response):

                # create the record using the mapping order, using
                data_list = [(k, row[mapping_order[k]]) for k in mapping_order.keys()]
                data = {k: v for k, v in data_list}
                # the syntax might be weird but end result generated dynamically
                # the record as airbyte expects and more or less has the following form
                # data = {
                # "account_name":"smth",
                # "account_code":"smth",
                # "level_name":"smth",
                # "dim1":"smth",
                # "dim2":"smth",
                # "...":"smth",
                # "amount.":"smth",
                # }

                # now add additional data in the record for the date,
                data.update({"date": date_selected})
                data.update({"version": version})

                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(
                        stream=self.generate_table_name(), data=data, emitted_at=int(datetime.now().timestamp()) * 1000
                    ),
                )
