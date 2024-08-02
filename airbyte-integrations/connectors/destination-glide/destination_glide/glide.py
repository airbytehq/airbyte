from abc import ABC, abstractmethod
import uuid
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

# TODO: to optimize batch size for variable number and size of columns, we could estimate row byte size based on the first row and choose a batch size based on that.
BATCH_SIZE = 500

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
    """
    An API client for interacting with a Glide Big Table. The intention is to
    create a new table or update an existing table including the table's schema
    and the table's rows.

    The protocol is to call `init`, `set_schema`, `add_rows` one or more times, and `commit` in that order.
    """

    def headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            f"Authorization": f"Bearer {self.api_key}"
        }

    def url(self, path: str) -> str:
        return f"{self.api_host}/{self.api_path_root + '/' if self.api_path_root != '' else ''}{path}"

    def init(self, api_key, table_name, api_host="https://api.glideapps.com", api_path_root=""):
        """
        Sets the connection information for the table.
        """
        self.api_host = api_host
        self.api_key = api_key
        self.api_path_root = api_path_root
        self.table_name = table_name
        # todo: validate args

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
    def create(cls) -> GlideBigTableBase:
        """
        Creates a new instance of the default implementation for the GlideBigTable API client.
        """
        return GlideBigTableRestStrategy()

class GlideBigTableRestStrategy(GlideBigTableBase):
    def reset(self):
        self.columns = None
        self.stash_id = str(uuid.uuid4())
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

    def raise_if_set_schema_not_called(self):
        if self.columns is None:
            raise ValueError(
                "set_schema must be called before add_rows or commit")

    def _add_row_batch(self, rows: List[BigTableRow]) -> None:
        logger.debug(f"Adding rows batch with size {len(rows)}")
        r = requests.post(
            self.url(f"stashes/{self.stash_id}/{self.stash_serial}"),
            headers=self.headers(),
            json=rows
            
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"failed to add rows batch for serial '{self.stash_serial}'. Response was '{r.text}'") from e  # nopep8

        logger.info(f"Added {len(rows)} rows as batch for serial '{self.stash_serial}' successfully.")  # nopep8
        self.stash_serial += 1

    def add_rows(self, rows: Iterator[BigTableRow]) -> None:
        self.raise_if_set_schema_not_called()
        batch = []
        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i:i + min(BATCH_SIZE, len(rows) - i)]
            self._add_row_batch(batch)

    def create_table_from_stash(self) -> None:
        logger.info(f"Creating new table for table name '{self.table_name}'...") # nopep8
        r = requests.post(
            self.url(f"tables"),
            headers=self.headers(),
            json={
                "name": self.table_name,
                "schema": {
                    "columns": self.columns
                },
                "rows": {
                    "$stashID": self.stash_id
                }
            }
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"failed to create table '{self.table_name}'. Response was '{r.text}'.") from e  # nopep8

        logger.info(f"Creating table '{self.table_name}' succeeded.")

    def overwrite_table_from_stash(self, table_id) -> None:
        # overwrite the specified table's schema and rows with the stash:
        r = requests.put(
            self.url(f"tables/{table_id}"),
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
            raise Exception(f"failed to overwrite table '{table_id}'. Response was '{r.text}'") from e  # nopep8

    def commit(self) -> None:
        self.raise_if_set_schema_not_called()
        # first see if the table already exists
        r = requests.get(
            self.url(f"tables"),
            headers=self.headers()
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"Failed to get table list. Response was '{r.text}'.") from e # nopep8

        found_table_id = None
        # confirm if table exists:
        body = r.json()
        if "data" not in body:
            raise Exception(f"get tables response did not include data in body. Status was: {r.status_code}: {r.text}.")  # nopep8

        for table in body["data"]:
            if table["name"] == self.table_name:
                found_table_id = table["id"]
                logger.info(f"Found existing table to reuse for table name '{self.table_name}' with ID '{found_table_id}'.")  # nopep8
                break

        if found_table_id != None:
            self.overwrite_table_from_stash(found_table_id)
        else:
            self.create_table_from_stash()

        logger.info(f"Successfully committed record stash for table '{self.table_name}' (stash ID '{self.stash_id}')")  # nopep8
