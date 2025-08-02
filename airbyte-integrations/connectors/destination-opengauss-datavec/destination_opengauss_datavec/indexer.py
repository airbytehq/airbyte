#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import os
from multiprocessing import Process
from typing import Optional

import psycopg2

from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import create_stream_identifier, format_exception
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from destination_opengauss_datavec.config import OpenGaussDatavecIndexingModel


CLOUD_DEPLOYMENT_MODE = "cloud"


class OpenGaussDataVecIndexer(Indexer):
    config: OpenGaussDatavecIndexingModel

    def __init__(self, config: OpenGaussDatavecIndexingModel, embedder_dimensions: int):
        super().__init__(config)
        self.embedder_dimensions = embedder_dimensions
        self._conn = None  # 初始化连接为None

    def __del__(self):
        """析构函数，确保连接被关闭"""
        self._close_connection()

    def _connect(self):
        """连接到OpenGauss"""
        try:
            self._conn = psycopg2.connect(
                dbname=self.config.database, 
                user=self.config.username, 
                password=self.config.password, 
                host=self.config.host, 
                port=self.config.port
            )
        except Exception as e:
            raise Exception(f"Failed to connect to database: {str(e)}")

    def _close_connection(self):
        """关闭数据库连接"""
        if hasattr(self, '_conn') and self._conn:
            try:
                self._conn.close()
            except Exception:
                pass  # 忽略关闭时的错误
            finally:
                self._conn = None

    def _check_schemas_exist(self):
        """检查配置的default schema是否存在"""
        if not hasattr(self.config, 'default_schema') or not self.config.default_schema:
            return
        
        # 分割多个schema（用逗号分隔）
        schemas = [schema.strip() for schema in self.config.default_schema.split(',')]
        missing_schemas = []
        
        try:
            with self._conn.cursor() as cur:
                for schema in schemas:
                    # 检查schema是否存在
                    cur.execute("""
                        SELECT 1 FROM information_schema.schemata 
                        WHERE schema_name = %s
                    """, (schema,))
                    
                    if cur.fetchone() is None:
                        missing_schemas.append(schema)
            
            # 如果有缺失的schema，抛出异常
            if missing_schemas:
                missing_list = ', '.join(missing_schemas)
                raise Exception(f"Schema(s) not found in database: {missing_list}. Please create them first.")
                
        except Exception as e:
            # 重新抛出异常，让上层处理
            raise Exception(f"Failed to check schemas: {str(e)}")

    def _connect_with_timeout(self):
        """带超时的连接测试，避免连接卡住"""
        def _test_connect():
            """测试连接的内部函数"""
            try:
                test_conn = psycopg2.connect(
                    dbname=self.config.database, 
                    user=self.config.username, 
                    password=self.config.password, 
                    host=self.config.host, 
                    port=self.config.port
                )
                test_conn.close()  # 立即关闭测试连接
            except Exception as e:
                raise Exception(f"Connection test failed: {str(e)}")
        
        # 在子进程中测试连接
        proc = Process(target=_test_connect)
        proc.start()
        proc.join(5)
        if proc.is_alive():
            # 如果5秒后进程还在运行，强制终止
            proc.terminate()
            proc.join()
            raise Exception("Connection timed out, please try again later or check your host and credentials")

    def _create_index(self, collection: Collection):
        """
        Create an index on the vector field when auto-creating the collection.

        This uses an IVF_FLAT index with 1024 clusters. This is a good default for most use cases. If more control is needed, the index can be created manually (this is also stated in the documentation)
        """
        collection.create_index(
            field_name=self.config.vector_field, index_params={"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 1024}}
        )

    def _create_client(self):
        """创建数据库客户端连接"""
        # 先关闭可能存在的旧连接
        self._close_connection()
        
        # 测试连接是否可达
        self._connect_with_timeout()
        
        # 在主进程中建立正式连接
        self._connect()

        

    def check(self) -> Optional[str]:
        """检查OpenGauss连接和表结构"""
        try:
            self._create_client()
            # 检查default schema是否存在
            self._check_schemas_exist()

        except Exception as e:
            return format_exception(e)
        return None

    def _uses_safe_config(self) -> bool:
        return self.config.host.startswith("https://") and not self.config.auth.mode == "no_auth"

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog) -> None:
        self._create_client()
        for stream in catalog.streams:
            if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                self._delete_for_filter(f'{METADATA_STREAM_FIELD} == "{create_stream_identifier(stream.stream)}"')

    def _delete_for_filter(self, expr: str) -> None:
        iterator = self._collection.query_iterator(expr=expr)
        page = iterator.next()
        while len(page) > 0:
            id_field = next(iter(page[0].keys()))
            ids = [next(iter(entity.values())) for entity in page]
            id_list_expr = ", ".join([str(id) for id in ids])
            self._collection.delete(expr=f"{id_field} in [{id_list_expr}]")
            page = iterator.next()

    def _normalize(self, metadata: dict) -> dict:
        result = {}

        for key, value in metadata.items():
            normalized_key = key
            # the primary key can't be set directly with auto_id, so we prefix it with an underscore
            if key == self._primary_key:
                normalized_key = f"_{key}"
            result[normalized_key] = value

        return result

    def index(self, document_chunks, namespace, stream):
        entities = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            entity = {
                **self._normalize(chunk.metadata),
                self.config.vector_field: chunk.embedding,
                self.config.text_field: chunk.page_content,
            }
            if chunk.page_content is not None:
                entity[self.config.text_field] = chunk.page_content
            entities.append(entity)
        self._collection.insert(entities)

    def delete(self, delete_ids, namespace, stream):
        if len(delete_ids) > 0:
            id_list_expr = ", ".join([f'"{id}"' for id in delete_ids])
            id_expr = f"{METADATA_RECORD_ID_FIELD} in [{id_list_expr}]"
            self._delete_for_filter(id_expr)
