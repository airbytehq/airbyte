"""Bucket implementation using SQLite
"""
import sqlite3
from threading import RLock
from typing import List
from typing import Optional
from typing import Tuple

from ..abstracts import AbstractBucket
from ..abstracts import Rate
from ..abstracts import RateItem


class Queries:
    CREATE_BUCKET_TABLE = """
    CREATE TABLE IF NOT EXISTS '{table}' (
        name VARCHAR,
        item_timestamp INTEGER
    )
    """
    CREATE_INDEX_ON_TIMESTAMP = """
    CREATE INDEX IF NOT EXISTS '{index_name}' ON '{table_name}' (item_timestamp)
    """
    COUNT_BEFORE_INSERT = """
    SELECT :interval{index} as interval, COUNT(*) FROM '{table}'
    WHERE item_timestamp >= :current_timestamp - :interval{index}
    """
    PUT_ITEM = """
    INSERT INTO '{table}' (name, item_timestamp) VALUES %s
    """
    LEAK = """
    DELETE FROM "{table}" WHERE rowid IN (
    SELECT rowid FROM "{table}" ORDER BY item_timestamp ASC LIMIT {count});
    """.strip()
    COUNT_BEFORE_LEAK = """SELECT COUNT(*) FROM '{table}' WHERE item_timestamp < {current_timestamp} - {interval}"""
    FLUSH = """DELETE FROM '{table}'"""
    # The below sqls are for testing only
    DROP_TABLE = "DROP TABLE IF EXISTS '{table}'"
    DROP_INDEX = "DROP INDEX IF EXISTS '{index}'"
    COUNT_ALL = "SELECT COUNT(*) FROM '{table}'"
    GET_ALL_ITEM = "SELECT * FROM '{table}' ORDER BY item_timestamp ASC"
    GET_FIRST_ITEM = "SELECT name, item_timestamp FROM '{table}' ORDER BY item_timestamp ASC"
    GET_LAG = """
    SELECT (strftime ('%s', 'now') || substr(strftime ('%f', 'now'), 4)) - (
    SELECT item_timestamp
    FROM '{table}'
    ORDER BY item_timestamp
    ASC
    LIMIT 1
    )
    """
    PEEK = 'SELECT * FROM "{table}" ORDER BY item_timestamp DESC LIMIT 1 OFFSET {count}'


class SQLiteBucket(AbstractBucket):
    """For sqlite bucket, we are using the sql time function as the clock
    item's timestamp wont matter here
    """

    rates: List[Rate]
    failing_rate: Optional[Rate]
    conn: sqlite3.Connection
    table: str
    full_count_query: str
    lock: RLock

    def __init__(self, rates: List[Rate], conn: sqlite3.Connection, table: str):
        self.conn = conn
        self.table = table
        self.rates = rates
        self.lock = RLock()

    def _build_full_count_query(self, current_timestamp: int) -> Tuple[str, dict]:
        full_query: List[str] = []

        parameters = {"current_timestamp": current_timestamp}

        for index, rate in enumerate(self.rates):
            parameters[f"interval{index}"] = rate.interval
            query = Queries.COUNT_BEFORE_INSERT.format(table=self.table, index=index)
            full_query.append(query)

        join_full_query = " union ".join(full_query) if len(full_query) > 1 else full_query[0]
        return join_full_query, parameters

    def put(self, item: RateItem) -> bool:
        with self.lock:
            query, parameters = self._build_full_count_query(item.timestamp)
            rate_limit_counts = self.conn.execute(query, parameters).fetchall()

            for idx, result in enumerate(rate_limit_counts):
                interval, count = result
                rate = self.rates[idx]
                assert interval == rate.interval
                space_available = rate.limit - count

                if space_available < item.weight:
                    self.failing_rate = rate
                    return False

            items = ", ".join([f"('{name}', {item.timestamp})" for name in [item.name] * item.weight])
            query = (Queries.PUT_ITEM.format(table=self.table)) % items
            self.conn.execute(query)
            self.conn.commit()
            return True

    def leak(self, current_timestamp: Optional[int] = None) -> int:
        """Leaking/clean up bucket"""
        with self.lock:
            assert current_timestamp is not None
            query = Queries.COUNT_BEFORE_LEAK.format(
                table=self.table,
                interval=self.rates[-1].interval,
                current_timestamp=current_timestamp,
            )
            count = self.conn.execute(query).fetchone()[0]
            query = Queries.LEAK.format(table=self.table, count=count)
            self.conn.execute(query)
            self.conn.commit()
            return count

    def flush(self) -> None:
        with self.lock:
            self.conn.execute(Queries.FLUSH.format(table=self.table))
            self.conn.commit()
            self.failing_rate = None

    def count(self) -> int:
        with self.lock:
            return self.conn.execute(Queries.COUNT_ALL.format(table=self.table)).fetchone()[0]

    def peek(self, index: int) -> Optional[RateItem]:
        with self.lock:
            query = Queries.PEEK.format(table=self.table, count=index)
            item = self.conn.execute(query).fetchone()

            if not item:
                return None

            return RateItem(item[0], item[1])

    @classmethod
    def init_from_file(cls, rates: List[Rate], table: str, create_new_table=True) -> "SQLiteBucket":
        sqlite_connection = sqlite3.connect(
            "./mydb.sqlite",
            isolation_level="EXCLUSIVE",
            check_same_thread=False,
        )
        if create_new_table:
            cursor = sqlite_connection.cursor()
            cursor.execute(Queries.CREATE_BUCKET_TABLE.format(table=table))

        return cls(
            rates,
            sqlite_connection,
            table=table,
        )
