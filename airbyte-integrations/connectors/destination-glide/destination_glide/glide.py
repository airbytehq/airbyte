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

DEFAULT_BATCH_SIZE = 1500

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

    The protocol is to call `init`, then `add_row` or `add_rows` one or more times, and finally, `commit`, in that order.
    """

    def headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            f"Authorization": f"Bearer {self.api_key}"
        }

    def url(self, path: str) -> str:
        return f"{self.api_host}/{self.api_path_root + '/' if self.api_path_root != '' else ''}{path}"

    def init(self, api_key, table_name, columns, api_host="https://api.glideapps.com", api_path_root="", batch_size = DEFAULT_BATCH_SIZE):
        """
        Sets the connection information for the table.
        """
        # todo: validate args
        self.api_key = api_key
        self.api_host = api_host
        self.api_path_root = api_path_root

        self.table_name = table_name
        self.columns = columns

        # TODO: to optimize batch size for variable number and size of columns, we could estimate row byte size based on the first row and choose a batch size based on that.
        self.batch_size = batch_size

    @abstractmethod
    def add_row(self, row: BigTableRow) -> None:
        """
        Adds a row to the table.
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
    def __init__(self):
        super().__init__()
        self.stash_id = str(uuid.uuid4())
        self.stash_serial = 0
        self.buffer = []

    def _flush_buffer(self):
        rows = self.buffer
        if len(rows) == 0:
            return
        self.buffer.clear()

        path = f"stashes/{self.stash_id}/{self.stash_serial}"
        logger.debug(f"Flushing {len(rows)} rows to {path} ...")
        r = requests.post(
            self.url(path),
            headers=self.headers(),
            json=rows
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"Failed to post rows batch to {path} : {r.text}") from e  # nopep8

        logger.info(f"Successfully posted {len(rows)} rows to {path}")  # nopep8
        self.stash_serial += 1

    def add_row(self, row: BigTableRow) -> None:
        self.buffer.append(row)
        if len(self.buffer) >= self.batch_size:
            self._flush_buffer()

    def add_rows(self, rows: Iterator[BigTableRow]) -> None:
        self.buffer.extend(rows)
        if len(self.buffer) >= self.batch_size:
            self._flush_buffer()

    def create_table_from_stash(self) -> None:
        logger.info(f"Creating new table '{self.table_name}' ...") # nopep8
        r = requests.post(
            self.url(f"tables?onSchemaError=dropColumns"),
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
            raise Exception(f"Failed to create table '{self.table_name}' : {r.text}") from e  # nopep8

        logger.info(f"Successfully created table '{self.table_name}'")

    def overwrite_table_from_stash(self, table_id) -> None:
        # overwrite the specified table's schema and rows with the stash:
        r = requests.put(
            self.url(f"tables/{table_id}?onSchemaError=dropColumns"),
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
            raise Exception(f"Failed to overwrite table '{table_id}' : {r.text}") from e  # nopep8

    def commit(self) -> None:
        # first see if the table already exists
        r = requests.get(
            self.url(f"tables"),
            headers=self.headers()
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"Failed to get table list: {r.text}") from e # nopep8

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

        # flush any remaining buffer to the stash
        self._flush_buffer()

        # commit the stash to the table
        if found_table_id != None:
            self.overwrite_table_from_stash(found_table_id)
        else:
            self.create_table_from_stash()

        logger.info(f"Successfully committed record stash for table '{self.table_name}' (stash ID '{self.stash_id}')")  # nopep8
