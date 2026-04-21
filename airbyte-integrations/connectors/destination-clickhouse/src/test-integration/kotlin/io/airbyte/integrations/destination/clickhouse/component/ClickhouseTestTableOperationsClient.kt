/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.component

import com.clickhouse.client.api.Client as ClickHouseClientRaw
import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
import com.clickhouse.data.ClickHouseFormat
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.util.serializeToString
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.future.await
import kotlinx.coroutines.withContext

private val logger = KotlinLogging.logger {}

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
        waitForPendingOperations(table)
        val qualifiedTableName = "`${table.namespace}`.`${table.name}`"
        client.query("SELECT * FROM $qualifiedTableName").await().use { resp ->
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

    /**
     * Wait for Clickhouse to finish processing the table. This is necessary for e.g. ALTER TABLE to
     * complete. If we don't do this, then we may receive a view of the table which does not reflect
     * its "latest" version.
     */
    private suspend fun waitForPendingOperations(table: TableName) {
        // force clickhouse to populate the operation into system.mutations
        client.execute("SYSTEM FLUSH LOGS")
        while (true) {
            val pendingOperations =
                client
                    .queryRecords(
                        """
                    SELECT *
                    FROM system.mutations
                    WHERE database = {database:String}
                      AND table = {table:String}
                    """.trimIndent(),
                        mapOf(
                            "database" to table.namespace,
                            "table" to table.name,
                        ),
                    )
                    .await()
                    .use { operations ->
                        operations
                            .filter { !it.getBoolean("is_done") }
                            .map { it.getString("command") }
                    }
            if (pendingOperations.isEmpty()) {
                logger.info { "No pending operations for table ${table.toPrettyString()}" }
                break
            } else {
                logger.info {
                    "Table ${table.toPrettyString()} has pending operations ($pendingOperations). Sleeping."
                }
                // we're probably calling this from within a runTest scope,
                // but we want to actually delay for real (since we're just waiting for clickhouse).
                // force this delay to run on a normal dispatcher.
                withContext(Dispatchers.IO) { delay(1000) }
            }
        }
    }
}
