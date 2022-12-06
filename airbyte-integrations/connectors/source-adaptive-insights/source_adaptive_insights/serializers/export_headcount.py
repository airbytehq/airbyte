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
        self.date = None
        self.headcount = None
        self.position = None
        self.location = None
        self.personel_input_type = None
        self.version = version

    @staticmethod
    def parse_date(date: str) -> str:
        try:
            return datetime.strptime(date, "%m/%Y").strftime("%Y-%m-%d")
        except Exception as e:
            return date

    def parse_row(self, row: dict) -> None:
        account_code = row.get("Account Code")
        level_name = row.get("Level Name")
        date = row.get("Date")
        location = row.get("Location Name")
        _id = f"{account_code}{level_name}{date}{gl_account}{location}{contract}{assignment}".encode("utf-8")
        self.id = int(hashlib.sha1(_id).hexdigest(), 16) % (10 ** 12)
        self.account_name = row.get("Account Name")
        self.account_code = account_code
        self.level_name = level_name
        self.date = self.parse_date(date)
        self.headcount = row.get("Headcount")
        self.location = location
        self.position = row.get("Position Name")
        self.personel_input_type = row.get("Personell_Input_Type Name")

    def to_record(self) -> dict:
        return {
            "id": self.id,
            "account_name": self.account_name,
            "account_code": self.account_code,
            "level": self.level_name,
            "location": self.location,
            "date": self.date,
            "position": self.position,
            "personel_input_type": self.personel_input_type,
            "version": self.version,
            "headcount": self.headcount,
        }

class DataProcessor:
    def __init__(self):
        self.file_path = os.path.join(os.getcwd(), f"{str(uuid4())}.csv")

    def process(self, response: str) -> None:
        
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
                "Location Name",
                "Personell_Input_Type Name",
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

        return self.file_path
        
        del df  # memory management

    def stream_file(self, chunk_size: int=1000) -> dict:
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
