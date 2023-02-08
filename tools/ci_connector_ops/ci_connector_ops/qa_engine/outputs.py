#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pandas as pd

from .models import ConnectorQAReport

def persist_qa_report(qa_report: pd.DataFrame, path: str, public_fields_only: bool =True):
    final_fields = [
        field.name for field in ConnectorQAReport.__fields__.values() 
        if field.field_info.extra["is_public"] or not public_fields_only
    ]
    qa_report[final_fields].to_json(path, orient="records")
