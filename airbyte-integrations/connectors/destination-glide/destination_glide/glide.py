from abc import ABC, abstractmethod
import requests
from typing import Dict, Any, Iterator, List

from .log import getLogger

logger = getLogger()

BigTableRow = Dict[str, Any]

ALLOWED_COLUMN_TYPES = [
    "string",
    "number",
    "boolean",
    "url",
    "dateTime",
    "json",
]

class Column:
    def __init__(self, id: str, type: str):
        if type not in ALLOWED_COLUMN_TYPES:
            raise ValueError(f"Column type {type} not allowed. Must be one of {ALLOWED_COLUMN_TYPES}")  # nopep8
        self._id = id
        self._type = type

    def id() -> str:
        return self._id

    def type() -> str:
        return self._type

    def to_json(self) -> Dict[str, Any]:
        return {
            'id': self._id,
            'type': self._type,
            'displayName': self._id
        }

    def __eq__(self, other):
        if isinstance(other, Column):
            return self._id == other._id and self._type == other._type
        return False

    def __repr__(self):
        return f"Column(id='{self._id}', type='{self._type}')"

class GlideBigTableBase(ABC):
    def headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            f"Authorization": f"Bearer {self.api_key}"
        }

    def url(self, path: str) -> str:
        return f"https://{self.api_host}/{self.api_path_root}/{path}"

    """
    An API client for interacting with a Glide Big Table.
    """

    def init(self, api_host, api_key, api_path_root, table_id):
        self.api_host = api_host
        self.api_key = api_key
        self.api_path_root = api_path_root
        self.table_id = table_id
        # todo: validate args
        pass

    @abstractmethod
    def prepare_table(self, columns: List[Column]) -> None:
        """
        Prepares the table with the given columns.
        Each column is a json-schema property where the key is the column name and the type is the .
        """
        pass

    @abstractmethod
    def rows(self) -> Iterator[BigTableRow]:
        """
        Gets the rows as of the Glide Big Table.
        """
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """
        Deletes all rows in the table.
        """
        pass

    def add_rows(self, rows: Iterator[BigTableRow]) -> None:
        """
        Adds rows to the table.
        """
        pass


def CreateBigTableDefaultImpl() -> GlideBigTableBase:
    """
    Creates a new instance of the default implementation for the GlideBigTable API client.
    """
    return GlideBigTableMutationsStrategy()


class GlideBigTableRestStrategy(GlideBigTableBase):

    def prepare_table(self, columns: List[Column]) -> None:
        logger.debug(f"prepare_table columns: {columns}")
        # update the table:
        r = requests.put(
            self.url(f"/tables/{self.table_id}"),
            headers=self.headers(),
            json={
                "name": self.table_id,
                "schema": {
                    "columns": columns,
                },
                "rows": []
            }
        )
        if r.status_code != 200:
            logger.error(f"prepare table request failed with status {r.status_code}: {r.text}.")  # nopep8

    def rows(self) -> Iterator[BigTableRow]:
        r = requests.get(
            self.url(f"/tables/{self.table_id}/rows"),
            headers=self.headers(),
        )
        if r.status_code != 200:
            logger.error(f"get rows request failed with status {r.status_code}: {r.text}.")  # nopep8 because https://github.com/hhatto/autopep8/issues/712
            r.raise_for_status()  # This will raise an HTTPError if the status is 4xx or 5xx

        result = r.json()

        # the result looks like an array of results; each result has a rows member that has an array or JSON rows:
        for row in result:
            for r in row['rows']:
                yield r

    def delete_all(self) -> None:
        logger.warning(f"delete_all call is ignored in {type(self).__class__.__name__}")  # nopep8
        pass

    def add_rows(self, rows: Iterator[BigTableRow]) -> None:
        r = requests.post(
            self.url(f"/tables/{self.table_id}/rows"),
            headers=self.headers(),
            json={
                "rows": list(rows)
            }
        )
        if r.status_code != 200:
            logger.error(f"get rows request failed with status {r.status_code}: {r.text}.")  # nopep8 because https://github.com/hhatto/autopep8/issues/712
            r.raise_for_status()  # This will raise an HTTPError if the status is 4xx or 5xx


class GlideBigTableMutationsStrategy(GlideBigTableBase):
    def __init__(self):
        # TODO: hardcoded for now using old api
        self.hardcoded_app_id = "Ix9CEuP6DiFugfjhSG5t"
        self.hardcoded_column_lookup = {
            '_airtable_id': {'type': "string", 'name': "Name"},
            '_airtable_created_time': {'type': "date-time", 'name': "AwkFL"},
            '_airtable_table_name': {'type': "string", 'name': "QF0zI"},
            'id': {'type': "string", 'name': "tLPjZ"},
            'name': {'type': "string", 'name': "1ZqF1"},
            'host_id': {'type': "string", 'name': "B7fYe"},
            'host_name': {'type': "string", 'name': "oyVzO"},
            'neighbourhood_group': {'type': "string", 'name': "15J8U"},
            'neighbourhood': {'type': "string", 'name': "Fy28U"},
            'latitude': {'type': "number", 'name': "TLpMC"},
            'longitude': {'type': "number", 'name': "oazQO"},
            'room_type': {'type': "string", 'name': "TPJDZ"},
            'price': {'type': "number", 'name': "7xzlG"},
            'minimum_nights': {'type': "number", 'name': "usoY5"},
            'number_of_reviews': {'type': "number", 'name': "XFXmR"},
            'last_review': {'type': "date-time", 'name': "oseZl"},
            'reviews_per_month': {'type': "number", 'name': "alw2R"},
            'calculated_host_listings_count': {'type': "number", 'name': "hKws0"},
            'availability_365': {'type': "number", 'name': "qZsgl"},
            'number_of_reviews_ltm': {'type': "number", 'name': "rWisS"},
            'license': {'type': "string", 'name': "7PVig"}
        }

    def headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            f"Authorization": f"Bearer {self.api_key}"
        }

    def url(self, path: str) -> str:
        return f"https://{self.api_host}/{self.api_path_root}/{path}"

    def prepare_table(self, columns: List[Column]) -> None:
        logger.debug(f"prepare_table for table '{self.table_id}. Expecting columns: '{[c.id for c in columns]}'.")
        self.delete_all()

        for col in columns:
            if col.id not in self.hardcoded_column_lookup:
                logger.warning(
                    f"Column '{col.id}' not found in hardcoded column lookup. Will be ignored.")

    def rows(self) -> Iterator[BigTableRow]:
        """
        Gets the rows as of the Glide Big Table.
        """
        r = requests.post(
            self.url("function/queryTables"),
            headers=self.headers(),
            json={
                "appID": self.hardcoded_app_id,
                "queries": [
                    {
                        "tableName": self.table_id,
                        "utc": True
                    }
                ]
            }
        )
        if r.status_code != 200:
            logger.error(f"get rows request failed with status {r.status_code}: {r.text}.")  # nopep8 because https://github.com/hhatto/autopep8/issues/712
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
                    "appID": self.hardcoded_app_id,
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
                logger.error(f"delete request failed with status {r.status_code}: {r.text} trying to delete row id {row['$rowID']} with row: {row}")  # nopep8 because https://github.com/hhatto/autopep8/issues/712
                r.raise_for_status() # This will raise an HTTPError if the status is 4xx or 5xx
            else:
                logger.debug(f"Deleted row successfully (rowID:'{row['$rowID']}'")

    def add_rows(self, rows: Iterator[BigTableRow]) -> None:
        # TODO: lame. need to batch mutations/requests
        mutations = []
        for row in rows:
            # row is columnLabel -> value, but glide's mutate uses a column "name". We hard-code the lookup for our table here:
            mutated_row = dict()
            for k, v in row.items():
                if k in self.hardcoded_column_lookup:
                    col_info = self.hardcoded_column_lookup[k]
                    mutated_row[col_info["name"]] = v
                else:
                    logger.error(
                        f"Column {k} not found in column lookup. Ignoring column")

            mutations.append(
                {
                    "kind": "add-row-to-table",
                    "tableName": self.table_id,
                    "columnValues": mutated_row
                }
            )
            r = requests.post(
                self.url("function/mutateTables"),
                headers=self.headers(),
                json={
                    "appID": self.hardcoded_app_id,
                    "mutations": mutations
                }
            )
        if r.status_code != 200:
            logger.error(f"add rows failed with status {r.status_code}: {r.text}")  # nopep8 because https://github.com/hhatto/autopep8/issues/712
            r.raise_for_status()  # This will raise an HTTPError if the status is 4xx or 5xx
