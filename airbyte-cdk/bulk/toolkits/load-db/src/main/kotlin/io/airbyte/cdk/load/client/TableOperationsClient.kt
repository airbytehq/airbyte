package io.airbyte.cdk.load.client

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations

interface TableOperationsClient :
    DirectLoadTableSqlOperations,
    DirectLoadTableNativeOperations {

    suspend fun ping() = Unit

    suspend fun namespaceExists(namespace: String) = false

    suspend fun dropNamespace(namespace: String) = Unit

    suspend fun tableExists(table: TableName) = false

    // for testing
    suspend fun insertRecords(table: TableName, records: List<Map<String, AirbyteValue>>) = Unit

    // for testing
    suspend fun readTable(table: TableName): List<Map<String, Any>> = listOf()
}
