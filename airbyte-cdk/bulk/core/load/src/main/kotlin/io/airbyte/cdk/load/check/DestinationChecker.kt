/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.check

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames

// TODO: Deprecate in favor if v2
interface DestinationChecker<C : DestinationConfiguration> {
    fun mockStream() =
        DestinationStream(
            unmappedNamespace = "testing",
            unmappedName = "test",
            importType = Append,
            schema = ObjectTypeWithoutSchema,
            generationId = 1,
            minimumGenerationId = 0,
            syncId = 1,
            namespaceMapper = NamespaceMapper(),
            tableSchema =
                StreamTableSchema(
                    tableNames = TableNames(finalTableName = TableName("testing", "test")),
                    columnSchema =
                        ColumnSchema(
                            inputSchema = mapOf(),
                            inputToFinalColumnNames = mapOf(),
                            finalSchema = mapOf(),
                        ),
                    importType = Append,
                )
        )

    fun check(config: C)
    fun cleanup(config: C) {}
}
