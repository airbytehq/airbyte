#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime

import pandas as pd

from .models import ConnectorQAReport


def persist_qa_report(qa_report: pd.DataFrame, path: str, public_fields_only: bool = True) -> str:
    report_generation_date = datetime.strftime(qa_report["report_generation_datetime"].max(), "%Y%m%d")
    path = path + f"{report_generation_date}_qa_report.jsonl"
    final_fields = [
        field.name for field in ConnectorQAReport.__fields__.values() if field.field_info.extra["is_public"] or not public_fields_only
    ]
    qa_report[final_fields].to_json(path, orient="records", lines=True)
    return path
