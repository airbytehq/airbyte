import requests
from typing import Dict, Any, Iterator

from .log import getLogger

logger = getLogger()

BigTableRow = Dict[str, Any]


class GlideBigTable:
    """
    An API client for interacting with a Glide Big Table.
    """

    def init(self, api_host, api_key, api_path_root, app_id, table_id):
        self.api_host = api_host
        self.api_key = api_key
        self.api_path_root = api_path_root
        self.app_id = app_id
        self.table_id = table_id
        # todo: validate args
        pass

    def headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            f"Authorization": f"Bearer {self.api_key}"
        }

    def url(self, path: str) -> str:
        return f"https://{self.api_host}/{self.api_path_root}/{path}"

    # todo: add type
    def rows(self) -> Iterator[BigTableRow]:
        """
        Gets the rows as of the Glide Big Table.
        """

        r = requests.post(
            self.url("function/queryTables"),
            headers=self.headers(),
            json={
                "appID": self.app_id,
                "queries": [
                    {
                        "tableName": self.table_id,
                        "utc": True
                    }
                ]
            }
        )
        if r.status_code != 200:
            logger.error(f"get rows request failed with status {r.status_code}: {r.text}.") # nopep8 because https://github.com/hhatto/autopep8/issues/712
            r.raise_for_status()  # This will raise an HTTPError if the status is 4xx or 5xx

        result = r.json()

        # the result looks like an array of results; each result has a rows member that has an array or JSON rows:
        for row in result:
            for r in row['rows']:
                yield r

    def delete_all(self) -> None:
        # TODO: perf: don't put these in a list
        rows = list(self.rows())
        logger.debug(f"Iterating over {len(rows)} rows to delete")

        for row in rows:
            # TODO: lame. batch these into one request with multiple mutations
            r = requests.post(
                self.url("function/mutateTables"),
                headers=self.headers(),
                json={
                    "appID": self.app_id,
                    "mutations": [
                        {
                            "kind": "delete-row",
                            "tableName": self.table_id,
                            "rowID": row['$rowID']
                        }
                    ]
                }
            )
            if r.status_code != 200:
                logger.error(f"delete request failed with status {r.status_code}: {r.text} trying to delete row id {row['$rowID']} with row: {row}") # nopep8 because https://github.com/hhatto/autopep8/issues/712
                r.raise_for_status()  # This will raise an HTTPError if the status is 4xx or 5xx

    def add_rows(self, row: BigTableRow) -> None:
        # TODO: lame. need to batch mutations/requests
        mutations = []
        for row in rows:
            # row is columnName -> value, but glide's mutate is value -> columnName so we fix that here:
            mutated_row = {v: k for k, v in row.items()}

            mutations.append({
                {
                    "kind": "add-row-to-table",
                    "tableName": self.table_id,
                    "columnValues": {
                        # TODO: kinda praying this row is the right shape 😅
                        mutated_row
                    }
                }
            })

        r = requests.post(
            self.url("function/mutateTables"),
            headers=self.headers(),
            json={
                "appID": self.app_id,
                "mutations": mutations
            }
        )
        if r.status_code != 200:
            logger.error(f"add rows failed with status {r.status_code}: {r.text}") # nopep8 because https://github.com/hhatto/autopep8/issues/712
            r.raise_for_status()  # This will raise an HTTPError if the status is 4xx or 5xx
