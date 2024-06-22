from abc import ABC, abstractmethod
from .log import LOG_LEVEL_DEFAULT
import logging
import requests
from typing import Dict, Any, Iterator, List

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL_DEFAULT)

BigTableRow = Dict[str, Any]

ALLOWED_COLUMN_TYPES = [
    "string",
    "number",
    "boolean",
    "url",
    "dateTime",
    "json",
]


class Column(dict):
    """
    Represents a Column in the glide API.
    NOTE: inherits from dict to be serializable to json.
    """

    def __init__(self, id: str, type: str):
        if type not in ALLOWED_COLUMN_TYPES:
            raise ValueError(f"Column type {type} not allowed. Must be one of {ALLOWED_COLUMN_TYPES}")  # nopep8
        dict.__init__(self, id=id, type={"kind": type}, displayName=id)

    def id(self) -> str:
        return self['id']

    def type(self) -> str:
        # NOTE: we serialize this as {kind: "<typename>"} per the rest API's serialization
        return self['type']['kind']

    def __eq__(self, other):
        if isinstance(other, Column):
            return dict(self) == dict(other)
        return False

    def __repr__(self):
        return f"Column(id='{self.id()}', type='{self.type()}')"


class GlideBigTableBase(ABC):
    def headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            f"Authorization": f"Bearer {self.api_key}"
        }

    def url(self, path: str) -> str:
        return f"{self.api_host}/{self.api_path_root}/{path}"

    """
    An API client for interacting with a Glide Big Table. The intention is to
    create a new table or update an existing table including the table's schema
    and the table's rows.

    The protocol is to call `init`, `set_schema`, `add_rows` one or more times, and `commit` in that order.
    """

    def init(self, api_host, api_key, api_path_root, table_id):
        """
        Sets the connection information for the table.
        """
        self.api_host = api_host
        self.api_key = api_key
        self.api_path_root = api_path_root
        self.table_id = table_id
        # todo: validate args
        pass

    @abstractmethod
    def set_schema(self, columns: List[Column]) -> None:
        """
        set_schemas the table with the given schema.
        Each column is a json-schema property where the key is the column name and the type is the .
        """
        pass

    @abstractmethod
    def add_rows(self, rows: Iterator[BigTableRow]) -> None:
        """
        Adds rows to the table.
        """
        pass

    @abstractmethod
    def commit(self) -> None:
        """
        Commits the table.
        """
        pass


class GlideBigTableFactory:
    """
    Factory for creating a GlideBigTableBase API client.
    """
    @classmethod
    def create(cls, strategy: str) -> GlideBigTableBase:
        """
        Creates a new instance of the default implementation for the GlideBigTable API client.
        """
        implementation_map = {
            "tables": GlideBigTableRestStrategy(),
            "mutations": GlideBigTableMutationsStrategy()
        }
        if strategy not in implementation_map:
            raise ValueError(f"Strategy '{strategy}' not found. Expected one of '{implmap.keys()}'.")  # nopep8
        return implementation_map[strategy]


class GlideBigTableRestStrategy(GlideBigTableBase):
    def reset(self):
        self.stash_id = None
        self.stash_serial = 0

    def __init__(self):
        super().__init__()
        self.reset()

    def set_schema(self, columns: List[Column]) -> None:
        logger.debug(f"set_schema columns: {columns}")
        if columns is None:
            raise ValueError("columns must be provided")
        if len(columns) == 0:
            raise ValueError("columns must be provided")
        self.reset()
        self.columns = columns
        # Create stash we can stash records into for later
        r = requests.post(
            self.url(f"/stashes"),
            headers=self.headers(),
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"failed to create stash") from e  # nopep8

        result = r.json()
        self.stash_id = result["data"]["stashID"]
        self.stash_serial = 0
        logger.info(f"Created stash for records with id '{self.stash_id}'")

    def raise_if_set_schema_not_called(self):
        if self.stash_id is None:
            raise ValueError(
                "set_schema must be called before add_rows or commit")

    def _add_row_batch(self, rows: List[BigTableRow]) -> None:
        # TODO: add rows to stash/serial https://web.postman.co/workspace/glideapps-Workspace~46b48d24-5fc1-44b6-89aa-8d6751db0fc5/request/9026518-c282ef52-4909-4806-88bf-08510ee80770
        logger.debug(f"Adding rows batch with size {len(rows)}")
        r = requests.post(
            self.url(f"/stashes/{self.stash_id}/{self.stash_serial}"),
            headers=self.headers(),
            json={
                "data": rows,
                "options": {
                    # ignore columns in rows that are not part of schema:
                    "unknownColumns": "ignore"
                }
            }
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"failed to add rows batch for serial '{self.stash_serial}'") from e  # nopep8

        logger.info(f"Add rows batch for serial '{self.stash_serial}' succeeded.")  # nopep8
        self.stash_serial += 1

    def add_rows(self, rows: Iterator[BigTableRow]) -> None:
        self.raise_if_set_schema_not_called()
        # TODO: to optimize batch size for variable number and size of columns, we could estimate row byte size based on the first row and choose a batch size based on that.
        BATCH_SIZE = 500
        batch = []
        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i:i + min(BATCH_SIZE, len(rows) - i)]
            self._add_row_batch(batch)

    def finalize_stash(self) -> None:
        # overwrite the existing table with the right schema and rows:
        r = requests.put(
            self.url(f"/tables/{self.table_id}"),
            headers=self.headers(),
            json={
                "schema": {
                    "columns": self.columns,
                },
                "rows": {
                    "$stashID": self.stash_id
                }
            }
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"failed to finalize stash") from e  # nopep8
        logger.info(f"Successfully finalized record stash for table '{self.table_id}' (stash ID '{self.stash_id}')")

    def commit(self) -> None:
        self.raise_if_set_schema_not_called()
        self.finalize_stash()


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
        return f"{self.api_host}/{self.api_path_root}/{path}"

    def set_schema(self, columns: List[Column]) -> None:
        logger.debug(f"set_schema for table '{self.table_id}. Expecting columns: '{[c.id for c in columns]}'.")  # nopep8
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
            r.raise_for_status()

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
                r.raise_for_status()
            else:
                logger.debug(
                    f"Deleted row successfully (rowID:'{row['$rowID']}'")

    def add_rows_batch(self, rows: Iterator[BigTableRow]) -> None:
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
            r.raise_for_status()

    def add_rows(self, rows: Iterator[BigTableRow]) -> None:
        BATCH_SIZE = 100

        batch = []
        for row in rows:
            batch.append(row)
            if len(batch) >= BATCH_SIZE:
                self.add_rows_batch(batch)
                batch = []

        if len(batch) > 0:
            self.add_rows_batch(batch)

    def commit(self) -> None:
        logger.debug("commit table (noop).")
        pass
