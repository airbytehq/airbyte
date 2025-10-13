/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load

import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations

interface CoreTableOperationsClient :
    AirbyteClient, DirectLoadTableSqlOperations, DirectLoadTableNativeOperations {

    suspend fun ping() = Unit

    suspend fun namespaceExists(namespace: String) = false

    suspend fun dropNamespace(namespace: String) = Unit

    suspend fun tableExists(table: TableName) = false
}
