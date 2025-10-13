/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.CoreTableOperationsClient
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import java.util.UUID
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.assertDoesNotThrow

interface CoreTableOperationsSuite {
    val client: CoreTableOperationsClient

    fun `connect to database`() = runTest {
        assertDoesNotThrow {  client.ping() }
    }

    fun `create and drop namespaces`() = runTest {
        val testNamespace = "namespace-test-${UUID.randomUUID()}"

        require(!client.namespaceExists(testNamespace)) { "test namespace: $testNamespace already exists. Please validate it's deleted before running again." }

        client.createNamespace(testNamespace)

        assert(client.namespaceExists(testNamespace))

        client.dropNamespace(testNamespace)

        assert(!client.namespaceExists(testNamespace))
    }

    fun `create and drop tables`() = runTest {
        val uniquePostFix = UUID.randomUUID()
        val testTable = TableName(
            "default",
            "table-test-table-$uniquePostFix",
        )

        require(!client.tableExists(testTable)) { "test table: ${testTable.namespace}.${testTable.name} already exists. Please validate it's deleted before running again." }

        client.createTable(
            stream = DestinationStream(
                unmappedNamespace = testTable.namespace,
                unmappedName = testTable.name,
                importType = Append,
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 1,
                includeFiles = false,
                schema = ObjectType(linkedMapOf()),
                namespaceMapper = NamespaceMapper(),
            ),
            tableName = testTable,
            columnNameMapping = ColumnNameMapping(mapOf()),
            replace = false,
        )

        assert(client.tableExists(testTable)) { "test table: ${testTable.namespace}.${testTable.name} was not created as expected." }

        client.dropTable(testTable)

        assert(!client.tableExists(testTable)) { "test table: ${testTable.namespace}.${testTable.name} was not dropped as expected." }
    }

    fun `count table rows`() {}

    fun `overwrite tables`() {}

    fun `copy tables`() {}

    fun `upsert tables`() {}

    fun `get generation id`() {}
}
