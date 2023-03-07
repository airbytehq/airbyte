from typing import Optional

import pandas as pd
from uuid import uuid4
import csv
import os
from datetime import datetime
from io import StringIO
import hashlib
import json


class Data:
    def __init__(self, version: str):
        self.id = None
        self.account_name = None
        self.account_code = None
        self.level_name = None
        self.position = None
        self.assignment = None
        self.location = None
        self.personnel_input_type = None
        self.date = None
        self.headcount = None
        self.version = version

    @staticmethod
    def parse_date(date: str) -> str:
        try:
            return datetime.strptime(date, "%m/%Y").strftime("%Y-%m-%d")
        except Exception as e:
            return date

    def parse_row(self, row: dict) -> None:
        self.account_name = row.get("Account Name")
        self.account_code = row.get("Account Code")
        self.level_name = row.get("Level Name")
        self.position = row.get("Position Name")
        self.assignment = row.get("Assignment Name")
        self.location = row.get("Location Name")
        self.personnel_input_type = row.get("Personnel_Input_Type Name")
        self.date = self.parse_date(row.get("Date"))
        self.headcount = row.get("Headcount")
        _id = f"" \
              f"{self.account_name}{self.account_code}{self.level_name}{self.position}" \
              f"{self.assignment}{self.location}" \
              f"{self.personnel_input_type}{self.date}".encode("utf-8")
        self.id = int(hashlib.sha1(_id).hexdigest(), 16) % (10 ** 12)

    def to_record(self) -> dict:
        return {
            "id": self.id,
            "account_name": self.account_name,
            "account_code": self.account_code,
            "level": self.level_name,
            "location": self.location,
            "assignment": self.assignment,
            "date": self.date,
            "position": self.position,
            "personnel_input_type": self.personnel_input_type,
            "version": self.version,
            "headcount": self.headcount,
        }


class DataProcessor:
    def __init__(self):
        self.file_path = os.path.join(os.getcwd(), f"{str(uuid4())}.csv")

    def process(self, response: str) -> Optional[str]:
        
        if not response:
            return None

        df = pd.read_csv(StringIO(response), sep=",")
        del response  # memory management

        df = df.melt(
            id_vars=[
                "Account Name",
                "Account Code",
                "Level Name",
                "Position Name",
                "Assignment Name",
                "Location Name",
                "Personnel_Input_Type Name",
            ],
            var_name="Date",
            value_name="Headcount"
        )

        df.to_csv(
            self.file_path, 
            quotechar='"', 
            quoting=csv.QUOTE_NONNUMERIC, 
            escapechar="\\",
            index=False
        )

        del df  # memory management

        return self.file_path

    def stream_file(self, chunk_size: int = 1000) -> dict:
        df_iter = pd.read_csv(self.file_path, chunksize=chunk_size)

        for chunk in df_iter:
            for row in json.loads(chunk.to_json(orient="records")):
                yield row

    def clean_csv(self):
        os.unlink(self.file_path)


def handle_export_headcount(response: dict, version: str) -> list:
    response = response.get("response").get("output")

    processor = DataProcessor()
    file_path = processor.process(response)
    print(response)

    if not file_path:
        return []

    records = []
    try:
        for stream_item in processor.stream_file():
            d = Data(version=version)
            d.parse_row(stream_item)
            records.append(d.to_record())
    except Exception as e:
        raise e
    finally:
        processor.clean_csv()  # always delete the file

    return records
