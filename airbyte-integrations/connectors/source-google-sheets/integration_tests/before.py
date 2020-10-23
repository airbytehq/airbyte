"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json

from apiclient import discovery

from google_sheets_source.models.generated.spreadsheet import Spreadsheet, SpreadsheetProperties, Sheet, GridData, CellData, RowData, SheetProperties
from google_sheets_source.helpers import Helpers

# Override default permission scopes to allow creating and editing spreadsheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file']
SECRETS_PATH = "../secrets/config.json"  # TODO replace with injected secrets


def before():
    with open(SECRETS_PATH, 'r') as file:
        config = json.loads(file.read())
    sheets_client = Helpers.get_authenticated_sheets_client(config, SCOPES)
    drive_client = Helpers.get_authenticated_drive_client(config, SCOPES)
    create_spreadsheet(sheets_client, drive_client)


def create_spreadsheet(sheets_client: discovery.Resource, drive_client: discovery):
    request = {
        "properties": {"title": f"integration_test_spreadsheet"},
        "sheets": [
            {"properties": {"title": "sheet1"}},
            {"properties": {"title": "sheet2"}}
        ]
    }

    spreadsheet = Spreadsheet.parse_obj(sheets_client.create(body=request).execute())
    spreadsheet_id = spreadsheet.spreadsheetId

    rows = [['header1', 'irrelevant', 'header3', '', 'ignored']]
    rows.extend([f"a{i}", "dontmindme", i] for i in range(300))
    rows.append(["lonely_left_value", "", ""])
    rows.append(["", "", "lonelyrightvalue"])
    rows.append(["", "", ""])
    rows.append(['orphan1', 'orphan2', 'orphan3'])

    sheets_client.values().batchUpdate(spreadsheetId=spreadsheet_id, body={"data": {"majorDimension": "ROWS", "values": rows, "ranges": "sheet1!1:1"}})
    sheets_client.values().batchUpdate(spreadsheetId=spreadsheet_id, body={"data": {"majorDimension": "ROWS", "values": rows, "ranges": "sheet2!1:1"}})

    # TODO remove this when test suite is ready. Just some manual print statements to verify teardown is working.
    print(sheets_client.get(spreadsheetId=spreadsheet_id, includeGridData=False).execute())
    print(drive_client.files().get(fileId=spreadsheet_id).execute())
    drive_client.files().delete(fileId=spreadsheet_id).execute()
    print(drive_client.files().get(fileId=spreadsheet_id).execute())

def destroy_spreadsheet():
    return


before()
