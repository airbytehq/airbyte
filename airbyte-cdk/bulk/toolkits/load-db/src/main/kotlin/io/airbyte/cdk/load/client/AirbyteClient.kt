/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.client

import io.airbyte.cdk.load.orchestration.db.TableName

interface AirbyteClient {
    /**
     * Returns the number of records in a specific table within a given database.
     *
     * @param database The name of the database.
     * @param table The name of the table.
     * @return The number of records in the specified table.
     */
    suspend fun countTable(tableName: TableName): Long?

    suspend fun createNamespace(namespace: String)
}
