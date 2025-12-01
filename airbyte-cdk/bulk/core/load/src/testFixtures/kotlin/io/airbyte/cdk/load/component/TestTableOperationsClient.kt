/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.schema.model.TableName

interface TestTableOperationsClient {
    /** Tests database connectivity. */
    suspend fun ping() = Unit

    /** Drops a namespace if it exists. */
    suspend fun dropNamespace(namespace: String) = Unit

    /**
     * Inserts records directly into a table for test verification. Do not use in production code -
     * use appropriate streaming mechanisms instead.
     */
    suspend fun insertRecords(table: TableName, records: List<Map<String, AirbyteValue>>) = Unit

    suspend fun insertRecords(table: TableName, vararg records: Map<String, AirbyteValue>) {
        insertRecords(table, records.toList())
    }

    /**
     * Reads all records from a table for test verification. Do not use in production code - this
     * loads entire table into memory.
     */
    suspend fun readTable(table: TableName): List<Map<String, Any>> = listOf()
}
