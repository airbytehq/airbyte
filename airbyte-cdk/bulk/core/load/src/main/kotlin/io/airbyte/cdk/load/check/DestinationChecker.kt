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

/**
 * A check operation that is run before the destination is used.
 *
 * * Implementors must provide a [check] method that validates the configuration.
 * * Implementors may provide a [cleanup] method that is run after the check is complete.
 * * [check] should throw an exception if the configuration is invalid.
 * * [cleanup] should not throw exceptions.
 * * Implementors should not perform any side effects in the constructor.
 * * Implementors should not throw exceptions in the constructor.
 * * Implementors should not inject configuration; only use the config passed in [check].
 */
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

// TODO the cleaner maybe should also be looking for old test tables, a la DestinationCleaner??
fun interface CheckCleaner<C : DestinationConfiguration> {
    fun cleanup(config: C, stream: DestinationStream)
}
