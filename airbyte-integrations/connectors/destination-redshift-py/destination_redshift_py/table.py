from typing import List, Optional

from destination_redshift_py.data_type_converter import VARCHAR, TIMESTAMP_WITHOUT_TIME_ZONE
from destination_redshift_py.field import Field, DataType

AIRBYTE_KEY_DATA_TYPE = DataType(name=VARCHAR, length="32")
AIRBYTE_AB_ID = Field(name="_airbyte_ab_id", data_type=AIRBYTE_KEY_DATA_TYPE)
AIRBYTE_EMITTED_AT = Field(name="_airbyte_emitted_at", data_type=DataType(name=TIMESTAMP_WITHOUT_TIME_ZONE))


class Table:
    def __init__(self, schema: str, name: str, fields: List[Field] = None, primary_keys: List[str] = None, references: "Table" = None):
        self.schema = schema
        self.name = name
        self.fields = [*(fields or list()), AIRBYTE_AB_ID, AIRBYTE_EMITTED_AT]

        self.primary_keys = [AIRBYTE_AB_ID.name, *(primary_keys or list())]

        self.references = references

    def create_statement(self) -> str:
        references = ""

        if self.references:
            reference_key = self.reference_key
            references = f", FOREIGN KEY({reference_key}) REFERENCES {self.references.schema}.{self.references.name}({AIRBYTE_AB_ID.name})"

            if reference_key not in self.field_names:
                self.fields.append(Field(name=reference_key, data_type=AIRBYTE_KEY_DATA_TYPE))

        fields = ", ".join(map(lambda field: field.__str__(), self.fields))
        primary_keys = f", PRIMARY KEY({', '.join(self.primary_keys)})"

        return f"""
            CREATE TABLE IF NOT EXISTS {self.schema}.{self.name} (
                {fields}{primary_keys}{references}, UNIQUE({AIRBYTE_AB_ID.name})  
            );
        """

    def coy_csv_gzip_statement(self, iam_role_arn: str, s3_full_path: str):
        return f"""
            COPY {self.schema}.{self.name}
            FROM '{s3_full_path}'
            iam_role '{iam_role_arn}'
            FORMAT CSV
            TIMEFORMAT 'auto'
            ACCEPTANYDATE
            IGNOREHEADER 1
            GZIP
        """

    @property
    def reference_key(self) -> Optional[str]:
        if self.references:
            return f"_airbyte_{self.references.name}_id"

    @property
    def field_names(self) -> List[str]:
        return list(map(lambda field: field.name, self.fields))
