from typing import List, Optional

from destination_redshift_py.data_type_converter import VARCHAR, TIMESTAMP_WITHOUT_TIME_ZONE
from destination_redshift_py.field import Field, DataType

AIRBYTE_ID_NAME = "_airbyte_ab_id"
AIRBYTE_EMITTED_AT_NAME = "_airbyte_emitted_at"

AIRBYTE_KEY_DATA_TYPE = DataType(name=VARCHAR, length="32")
AIRBYTE_AB_ID = Field(name=AIRBYTE_ID_NAME, data_type=AIRBYTE_KEY_DATA_TYPE)
AIRBYTE_EMITTED_AT = Field(name=AIRBYTE_EMITTED_AT_NAME, data_type=DataType(name=TIMESTAMP_WITHOUT_TIME_ZONE))


class Table:
    def __init__(self, schema: str, name: str, fields: List[Field] = None, primary_keys: List[str] = None, references: "Table" = None):
        self.schema = schema
        self.name = name
        self.fields = [*(fields or list()), AIRBYTE_AB_ID, AIRBYTE_EMITTED_AT]

        self.primary_keys = [AIRBYTE_AB_ID.name, *(primary_keys or list())]

        self.references = references

    @property
    def full_name(self) -> str:
        return f"{self.schema}.{self.name}"

    @property
    def reference_key(self) -> Optional[Field]:
        if self._reference_key_name:
            return Field(name=self._reference_key_name, data_type=AIRBYTE_KEY_DATA_TYPE)

    @property
    def field_names(self) -> List[str]:
        return list(map(lambda field: field.name, self.fields))

    def create_statement(self, staging: bool = False) -> str:
        primary_keys = f", PRIMARY KEY({', '.join(self.primary_keys)})"

        foreign_key = ""
        if self.references:
            reference_key = self.reference_key
            foreign_key = f", FOREIGN KEY({reference_key.name}) REFERENCES {self.references.full_name}({AIRBYTE_ID_NAME})"

            if reference_key.name not in self.field_names:
                self.fields.append(reference_key)

        fields = ", ".join(map(lambda field: str(field), self.fields))

        return f"""
            CREATE TABLE IF NOT EXISTS {self.schema}.{self.name} (
                {fields}{primary_keys}{foreign_key},
                UNIQUE({AIRBYTE_AB_ID.name})
            )
            BACKUP {'NO' if staging else 'YES'}
            DISTKEY({AIRBYTE_ID_NAME})
            SORTKEY ({AIRBYTE_EMITTED_AT_NAME});
        """

    def truncate_statement(self) -> str:
        return f"TRUNCATE TABLE {self.full_name}"

    def copy_csv_gzip_statement(self, iam_role_arn: str, s3_full_path: str) -> str:
        return f"""
            COPY {self.schema}.{self.name}
            FROM '{s3_full_path}'
            iam_role '{iam_role_arn}'
            FORMAT CSV
            TIMEFORMAT 'auto'
            ACCEPTANYDATE
            TRUNCATECOLUMNS
            IGNOREHEADER 1
            GZIP
        """

    def upsert_statements(self, staging_table: "Table") -> str:
        delete_condition = " AND ".join(
            [f"staging.{column} = {self.name}.{column}" for column in self.primary_keys]
        )

        delete_from_final_table = f"""
            DELETE FROM {self.schema}.{self.name}
            USING {staging_table.schema}.{staging_table.name} AS staging WHERE {delete_condition}
        """

        insert_into_final_table = f"""
            INSERT INTO {self.schema}.{self.name}
            SELECT * FROM {staging_table.schema}.{staging_table.name}
        """

        truncate_staging_table = f"TRUNCATE TABLE {staging_table.schema}.{staging_table.name}"

        return f"{delete_from_final_table};{insert_into_final_table};{truncate_staging_table};"

    @property
    def _reference_key_name(self) -> Optional[str]:
        if self.references:
            return f"_airbyte_{self.references.name}_id"
