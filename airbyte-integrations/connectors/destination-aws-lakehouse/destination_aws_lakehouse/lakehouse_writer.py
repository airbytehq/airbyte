
import awswrangler as wr
import logging
import boto3
import json
import re
from .config_reader import ConnectorConfig,PartitionOptions,IcebergPartitionType
from airbyte_cdk.models import DestinationSyncMode,ConfiguredAirbyteStream,SyncMode
import string
import random
from airbyte_cdk import AirbyteLogger
from pandas import DataFrame
from datetime import date, datetime
import pandas as pd
from .handler import Handler
from typing import Any, Dict, List, Optional, Tuple, Union
from botocore.exceptions import ClientError
import numpy
from decimal import Decimal, getcontext
from .constants import EMPTY_VALUES, GLUE_TYPE_MAPPING_DECIMAL, GLUE_TYPE_MAPPING_DOUBLE, PANDAS_TYPE_MAPPING

logger = logging.getLogger('airbyte')

class DictEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)

        if isinstance(obj, (pd.Timestamp, datetime)):
            # all timestamps and datetimes are converted to UTC
            return obj.strftime("%Y-%m-%dT%H:%M:%SZ")

        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")

        return super(DictEncoder, self).default(obj)

class LakehouseWriter:

    def __init__(self,handler:Handler,config:ConnectorConfig,configured_stream: ConfiguredAirbyteStream) -> None:
        
        self._config = config
        self.stream_name = configured_stream.stream.name
        self._configured_stream: ConfiguredAirbyteStream = configured_stream
        self.glue_database_name = self._config.glue_database
        self.glue_catalog_uri = f"s3://{config.bucket_name}/{config.bucket_prefix}"  # Replace with your Glue Catalog URI
        self.temp_bucket = self._config.temp_bucket
        self.temp_table_name = f"_temp_{''.join(random.choices(string.ascii_letters, k=10))}"
        self.temp_s3_path = f"s3://{self.temp_bucket}/{self.temp_table_name}/{self.stream_name or '_check'}"
        self.handler = handler
        self._messages = []
        self._schema: Dict[str, Any] = {k.replace(" ","_"): v for k, v in self._configured_stream.stream.json_schema["properties"].items()} #configured_stream.stream.json_schema["properties"]
        self._schema_clean: Dict[str, Any] = {}
        self._total_messages = 0
        self.glue_database_exists = False

        self.set_clean_schema()

        print(configured_stream.stream)
        
    def _create_database(self) -> bool:

        sql = f"create database if not exists {self.glue_database_name}"
        wr.athena.start_query_execution(sql=sql,wait=True)

        self.glue_database_exists = True

        return True
    
    def _clean_column_name(self,column_name):
        # Remove special characters from cloumn names
        cleaned_name = re.sub(r'[^a-zA-Z0-9_]', '', column_name)
        return cleaned_name

    # in case the column name contains special chars, they will be removed    
    def set_clean_schema(self):

        self._schema_clean = {self._clean_column_name((k.replace(" ","_"))): v for k, v in self._configured_stream.stream.json_schema["properties"].items()} #configured_stream.stream.json_schema["properties"]
        self._configured_stream.cursor_field = [self._clean_column_name(item) for item in self._configured_stream.cursor_field]
    
    def write_to_s3(self) -> None:

        # create db if it doesn't exist
        if not self.glue_database_exists:
            self._create_database()

        dtypes, json_casts = self._get_iceberg_dtypes_from_json_schema(self._schema_clean)
        if len(self._messages) > 0:
                
            df = pd.DataFrame(self._messages)

            # in case when the column names have special charchters, they will be renamed
            source_schema = self._schema.keys()
            clean_schema = self._schema_clean.keys()
            # Create the dictionary with swapped positions
            renamed_columns = {value: key for key, value in zip(clean_schema,source_schema)}
            df=df.rename(columns=renamed_columns)


            # Make sure complex types that can't be converted
            # to a struct or array are converted to a json string
            # so they can be queried with json_extract
            for col in json_casts:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: json.dumps(x, cls=DictEncoder))
            wr.s3.to_parquet(
                df=df,
                dataset=True,
                database=self.glue_database_name,
                path=self.temp_s3_path,
                table=self.temp_table_name,
                dtype=dtypes,
                mode='append'
            )

        self._messages.clear()
    
    def _drop_additional_top_level_properties(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper that removes any unexpected top-level properties from the record.
        Since the json schema is used to build the table and cast types correctly,
        we need to remove any unexpected properties that can't be casted accurately.
        """
        schema_keys = self._schema.keys()
        records_keys = record.keys()
        difference = list(set(records_keys).difference(set(schema_keys)))

        for key in difference:
            del record[key]

        return record
    
    def append_message(self, message: Dict[str, Any]):
        clean_message = self._drop_additional_top_level_properties(message)
        clean_message = self._json_schema_cast(clean_message)
        self._messages.append(clean_message)

    def _json_schema_cast(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper that fixes obvious type violations in a record's top level keys that may
        cause issues when casting data to pyarrow types. Such as:
        - Objects having empty strings or " " or "-" as value instead of null or {}
        - Arrays having empty strings or " " or "-" as value instead of null or []
        """
        for key, schema_type in self._schema.items():
            typ = self._schema[key].get("type")
            typ = self._get_json_schema_type(typ)
            record[key] = self._json_schema_cast_value(record.get(key), schema_type)

        return record
    
    def _json_schema_cast_value(self, value, schema_entry) -> Any:
        typ = schema_entry.get("type")
        typ = self._get_json_schema_type(typ)
        props = schema_entry.get("properties")
        items = schema_entry.get("items")

        if typ == "string":
            format = schema_entry.get("format")
            if format == "date-time":
                return pd.to_datetime(value, errors="coerce", utc=True)

            return str(value) if value and value != "" else None

        elif typ == "integer":
            return pd.to_numeric(value, errors="coerce")

        elif typ == "number":
            # if self._config.glue_catalog_float_as_decimal:
            #     return Decimal(str(value)) if value else Decimal("0")
            return pd.to_numeric(value, errors="coerce")

        elif typ == "boolean":
            return bool(value)

        elif typ == "null":
            return None

        elif typ == "object":
            if value in EMPTY_VALUES:
                return None

            if isinstance(value, dict) and props:
                for key, val in value.items():
                    if key in props:
                        value[key] = self._json_schema_cast_value(val, props[key])
                return value

        elif typ == "array" and items:
            if value in EMPTY_VALUES:
                return None

            if isinstance(value, list):
                return [self._json_schema_cast_value(item, items) for item in value]

        return value

    # create a table to store the temp data
    def create_temp_athena_table(self,df) -> None:

        rnd = random.choices(string.ascii_letters, k=10)
        dtypes, _ =self._get_iceberg_dtypes_from_json_schema(self._schema),
        wr.s3.to_parquet(
            df=df,
            dataset=False,
            database=self.glue_database_name,
            path=f"{self.temp_s3_path}/{rnd}.parquet",
            table=self.temp_table_name,
            dtype=dtypes,
            mode='append'
        )

    def temp_table_cleanup(self) -> None:

        # drop the temp athena table
        drop_table_query = f"drop table `{self.temp_table_name}`"
        wr.athena.start_query_execution(
            sql=drop_table_query,
            database=self.glue_database_name,
            wait=True
        )

        # delete the data from s3
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.temp_bucket)
        bucket.objects.filter(Prefix=f"{self.temp_table_name}/").delete()

    def reset(self):
        logger.info(f"Deleting table {self._database}:{self._table}")
        success = self.handler.temp_table_cleanup(self._database, self._table)

        if not success:
            logger.warning(f"Failed to reset table {self._database}:{self._table}")
    
    def _is_invalid_struct_or_array(self, schema: Dict[str, Any]) -> bool:
        """
        Helper that detects issues with nested objects/arrays in the json schema.
        When a complex data type is detected (schema with oneOf) or a nested object without properties
        the columns' dtype will be casted to string to avoid pyarrow conversion issues.
        """
        result = True

        def check_properties(schema):
            nonlocal result
            for val in schema.values():
                # Complex types can't be casted to an athena/glue type
                if val.get("oneOf"):
                    result = False
                    continue

                raw_typ = val.get("type")

                # If the type is a list, check for mixed types
                # complex objects with mixed types can't be reliably casted
                if isinstance(raw_typ, list) and self._json_schema_type_has_mixed_types(raw_typ):
                    result = False
                    continue

                typ = self._get_json_schema_type(raw_typ)

                # If object check nested properties
                if typ == "object":
                    properties = val.get("properties")
                    if not properties:
                        result = False
                    else:
                        check_properties(properties)

                # If array check nested properties
                if typ == "array":
                    items = val.get("items")

                    if not items:
                        result = False
                        continue

                    if isinstance(items, list):
                        items = items[0]

                    item_properties = items.get("properties")
                    if item_properties:
                        check_properties(item_properties)

        check_properties(schema)
        return result
    
    def _get_non_null_json_schema_types(self, typ: Union[str, List[str]]) -> Union[str, List[str]]:
        if isinstance(typ, list):
            return list(filter(lambda x: x != "null", typ))

        return typ
    
    def _json_schema_type_has_mixed_types(self, typ: Union[str, List[str]]) -> bool:
        if isinstance(typ, list):
            typ = self._get_non_null_json_schema_types(typ)
            if len(typ) > 1:
                return True

        return False
    
    def _get_json_schema_type(self, types: Union[List[str], str]) -> str:
        if isinstance(types, str):
            return types

        if not isinstance(types, list):
            return "string"

        types = self._get_non_null_json_schema_types(types)
        # when multiple types, cast to string
        if self._json_schema_type_has_mixed_types(types):
            return "string"

        return types[0]
    
    def _get_iceberg_dtypes_from_json_schema(self, schema: Dict[str, Any]) -> Tuple[Dict[str, str], List[str]]:
        """
        Helper that infers iceberg(athena) dtypes from a json schema.
        """

        column_types = {}
        json_columns = set()
        for col, definition in schema.items():
            result_typ = None
            col_typ = definition.get("type")
            airbyte_type = definition.get("airbyte_type")
            col_format = definition.get("format")

            col_typ = self._get_json_schema_type(col_typ)

            # special case where the json schema type contradicts the airbyte type
            if col_typ == "integer":
                result_typ = "int"

            if airbyte_type and col_typ == "number" and airbyte_type == "integer":
                col_typ = "int"

            if airbyte_type == "integer" and col_typ == "number":
                result_typ = "int"
            
            if col_typ == "number" and airbyte_type != "integer":
                result_typ = "double"

            if col_typ == "string" and col_format == "date-time":
                result_typ = "timestamp"

            if col_typ == "string" and col_format == "date":
                result_typ = "date"

            if col_typ == "boolean":
                result_typ = "boolean"

            if col_typ == "object":
                json_columns.add(col)
                result_typ = "string"
                # properties = definition.get("properties")
                # allow_additional_properties = definition.get("additionalProperties", False)
                # if properties and not allow_additional_properties and self._is_invalid_struct_or_array(properties):
                #     object_props = self._get_iceberg_dtypes_from_json_schema(properties)
                #     result_typ = f"struct<{','.join([f'{k}:{v}' for k, v in object_props.items()])}>"
                # else:
                #     json_columns.add(col)
                #     result_typ = "string"

            if col_typ == "array":
                items = definition.get("items", {})

                if isinstance(items, list):
                    items = items[0]

                raw_item_type = items.get("type")
                airbyte_raw_item_type = items.get("airbyte_type")

                # special case where the json schema type contradicts the airbyte type
                if airbyte_raw_item_type and raw_item_type == "number" and airbyte_raw_item_type == "integer":
                    raw_item_type = "int"

                item_type = self._get_json_schema_type(raw_item_type)
                item_properties = items.get("properties")

                # if array has no "items", cast to string
                if not items:
                    json_columns.add(col)
                    result_typ = "string"

                # if array with objects
                elif isinstance(items, dict) and item_properties:
                    # Check if nested object has properties and no mixed type objects
                    if self._is_invalid_struct_or_array(item_properties):
                        item_dtypes,_ = self._get_iceberg_dtypes_from_json_schema(item_properties)
                        inner_struct = f"struct<{','.join([f'{k}:{v}' for k, v in item_dtypes.items()])}>"
                        result_typ = f"array<{inner_struct}>"
                    else:
                        json_columns.add(col)
                        result_typ = "string"

                elif item_type and self._json_schema_type_has_mixed_types(raw_item_type):
                    json_columns.add(col)
                    result_typ = "string"

            if result_typ is None:
                result_typ = 'string'
            
            # if the cursor field is a string, it has to be converted to a timestamp
            if self._configured_stream.destination_sync_mode == SyncMode.incremental:
                if col == self._configured_stream.cursor_field[0] and \
                    result_typ == 'string':
                    result_typ = 'timestamp'


            column_types[col] = result_typ

            # if it's the partition column and it's not a datetime data type. a datetime type will be forced
            if len(self._configured_stream.cursor_field) > 0:
                if self._config.iceberg_is_partitioned and col == self._configured_stream.cursor_field[0]:
                    column_types[col] = 'timestamp'

        return column_types,json_columns
    
    def _add_iceberg_partition(self) -> str:

        if len(self._configured_stream.cursor_field) > 0:
            if self._config.iceberg_is_partitioned:
                fields = ",".join(self._configured_stream.cursor_field)
                return f"{self._config.iceberg_partition_type.value}({fields})"
            
    import re

        
    def _get_schema_fields_with_dtype(self):

        columns,_ = self._get_iceberg_dtypes_from_json_schema(self._schema_clean)
        fields = x = ', '.join(f'{self._clean_column_name(field)} {columns[field]}' for field in columns)

        return fields
    
    def _get_create_table_sql_statement(self) -> str:

        iceberg_partitions = self._add_iceberg_partition()
        partitions = f"PARTITIONED BY ({iceberg_partitions})"
        
        print(f'cursor field for stream: {self.stream_name}',self._configured_stream.cursor_field)
        if iceberg_partitions:
            return f"""create table {self.stream_name} (
                    {self._get_schema_fields_with_dtype()}
                    )
                    {partitions}
                    LOCATION '{self.glue_catalog_uri}/{self.stream_name}'
                    TBLPROPERTIES ( 'table_type' ='ICEBERG'  )
            """
        else:
            return f"""create table {self.stream_name} (
                    {self._get_schema_fields_with_dtype()}
                    )
                    LOCATION '{self.glue_catalog_uri}/{self.stream_name}'
                    TBLPROPERTIES ( 'table_type' ='ICEBERG'  )
            """
    
    def _table_exists(self, database: str, table: str) -> bool:
        try:
            self.handler.glue_client.get_table(DatabaseName=database, Name=table)
            return True
        except ClientError:
            return False
    
    def _create_iceberg_table(self):

        if not self._table_exists(self.glue_database_name,self.stream_name):
            sql_create_statement = self._get_create_table_sql_statement()
            print('create table:',self.stream_name)
            print(sql_create_statement)
            wr.athena.start_query_execution(sql=sql_create_statement,database=self.glue_database_name,wait=True)
        else:
            logger.info(f"table {self.stream_name} exists in database {self.glue_database_name}")

    def _get_iceberg_partition_date_cast_type(self):

        partition_type = self._config.iceberg_partition_type

        if partition_type == IcebergPartitionType.DATE:
            return 'yyyy-mm-dd'
        elif partition_type == IcebergPartitionType.MONTH:
            return 'yyyy-mm'
        elif partition_type == IcebergPartitionType.YEAR:
            return 'yyyy'

    def _get_partitions(self) -> list:

        sql = f"""
            select distinct 
                to_char({self._configured_stream.cursor_field[0]},'{self._get_iceberg_partition_date_cast_type()}') as part
            from "{self.temp_table_name}"
            order by 1
            """
        
        return wr.athena.read_sql_query(sql=sql,
                        database=self.glue_database_name,
                        ctas_approach=False)['part'].to_list()
    
    def _append_to_destination(self,date_from:str,date_to:str) -> None:

        sql = f"""
            insert into {self.stream_name} ({', '.join(f'"{field}"' for field in self._schema_clean)})
            select {', '.join(f'"{self._clean_column_name(field)}"' for field in self._schema_clean)}
            from {self.temp_table_name}
            where {self._clean_column_name(self._configured_stream.cursor_field[0])} >= timestamp '{date_from} 00:00:00'
                and {self._clean_column_name(self._configured_stream.cursor_field[0])} <= timestamp '{date_to} 23:59:59'
        """

        wr.athena.start_query_execution(sql=sql,
                                        database=self.glue_database_name,
                                        wait=True)

    def _create_merge_key(self):

        primary_key = self._configured_stream.primary_key
        if primary_key is None:
            primary_key= self._configured_stream.source_defined_primary_key

        merge_key = ' and '.join(f'tgt.{field[0]}=src.{field[0]}' for field in primary_key)
        primary_keys = [field[0] for field in primary_key]

        return merge_key,primary_keys

    def _merge_to_destination(self,date_from:str,date_to:str) -> None:

        
        # Dedup the records
        merge_key,primary_keys = self._create_merge_key()
        dedup_join = ' and '.join(f'dedup.{field}=tmp.{field}' for field in primary_keys)
        sql = f"""
            MERGE INTO {self.stream_name} AS tgt
            USING (
                with dedup as (
                    select {','.join(primary_keys)},
                    {self._clean_column_name(self._configured_stream.cursor_field[0])} cursor,
                    rank() over (partition by {','.join(primary_keys)} order by {self._clean_column_name(self._configured_stream.cursor_field[0])} desc) rk
                    from {self.temp_table_name} tmp
                )
                select {', '.join(f'tmp."{field}"' for field in self._schema)}
                from {self.temp_table_name} tmp
                join dedup on {dedup_join}
                    and tmp.{self._clean_column_name(self._configured_stream.cursor_field[0])} = dedup.cursor
                    and dedup.rk = 1 --take only the latest row for of the primary key(s)
                where tmp.{self._clean_column_name(self._configured_stream.cursor_field[0])} >= timestamp '{date_from} 00:00:00'
                    and tmp.{self._clean_column_name(self._configured_stream.cursor_field[0])} <= timestamp '{date_to} 23:59:59'
            ) AS src
            ON ({merge_key})
            WHEN MATCHED
            THEN UPDATE SET
            {', '.join(f'{field}=src.{field}' for field in self._schema if field not in primary_keys)}
            WHEN NOT MATCHED
            THEN INSERT ({', '.join(f'{field}' for field in self._schema)})
            VALUES ({', '.join(f'src.{field}' for field in self._schema)})
        """

        wr.athena.start_query_execution(sql=sql,
                                        database=self.glue_database_name,
                                        wait=True)

    def _append_with_partitions(self,append_type:DestinationSyncMode) -> None:

        partitions = self._get_partitions()
        chunks = [partitions[x:x+100] for x in range(0, len(partitions), 100)]

        for chunk in chunks:
            date_from = chunk[0]
            date_to = chunk[-1]
            if append_type == DestinationSyncMode.append:
                self._append_to_destination(date_from=date_from,date_to=date_to)
            elif append_type == DestinationSyncMode.append_dedup:
                self._merge_to_destination(date_from=date_from,date_to=date_to)

    def _full_refresh(self) -> None:

        # if DestinationSyncMode is Overwrite then first truncate the destination table
        if self._configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
            delete_sql = f"delete from {self.stream_name}"
            wr.athena.start_query_execution(sql=delete_sql,
                                            database=self.glue_database_name,
                                            wait=True)
            
        insert_sql = f"""
            insert into {self.stream_name} ({', '.join(f'"{field}"' for field in self._schema_clean)})
            select {', '.join(f'"{field}"' for field in self._schema_clean)}
            from {self.temp_table_name}
        """

        wr.athena.start_query_execution(sql=insert_sql,
                                        database=self.glue_database_name,
                                        wait=True)

    def merge_to_iceberg(self):

        # create database if it doesn't exist
        self._create_database()
        
        self._create_iceberg_table()

        if self._configured_stream.sync_mode == SyncMode.incremental:
            self._append_with_partitions(self._configured_stream.destination_sync_mode)
        elif self._configured_stream.sync_mode == SyncMode.full_refresh:
            self._full_refresh()

        self.temp_table_cleanup()