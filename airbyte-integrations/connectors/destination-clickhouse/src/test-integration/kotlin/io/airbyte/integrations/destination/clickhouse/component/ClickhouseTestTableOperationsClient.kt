/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.component

import com.clickhouse.client.api.Client as ClickHouseClientRaw
import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
import com.clickhouse.data.ClickHouseFormat
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.util.serializeToString
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import kotlinx.coroutines.future.await

@Requires(env = ["component"])
@Singleton
class ClickhouseTestTableOperationsClient(
    private val client: ClickHouseClientRaw,
) : TestTableOperationsClient {
    override suspend fun ping() {
        client.execute("SELECT 1").await()
    }

    override suspend fun dropNamespace(namespace: String) {
        client.execute("DROP DATABASE IF EXISTS `$namespace`").await()
    }

    override suspend fun insertRecords(table: TableName, records: List<Map<String, AirbyteValue>>) {
        client
            .insert(
                "`${table.namespace}`.`${table.name}`",
                records.serializeToString().byteInputStream(),
                ClickHouseFormat.JSONEachRow,
            )
            .await()
    }

    override suspend fun readTable(table: TableName): List<Map<String, Any>> {
        val qualifiedTableName = "`${table.namespace}`.`${table.name}`"
        val resp = client.query("SELECT * FROM $qualifiedTableName").await()
        val schema = client.getTableSchema(qualifiedTableName)

        val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(resp, schema)

        val records = mutableListOf<Map<String, Any>>()
        while (reader.hasNext()) {
            // get next record
            val cursor = reader.next()
            // create immutable copy
            val record = cursor.toMap()

            records.add(record)
        }
        return records
    }
}
