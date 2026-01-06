/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.DefaultDestinationCatalogFactory
import io.airbyte.cdk.load.command.DestinationStreamFactory
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.schema.TableNameResolver
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest

/**
 * This suite implements generic test cases for how destination connectors handle unusual names
 * (including table names, table namespaces, and column names). Most of these test cases simply
 * validate that the connector is capable of creating a table with the given identifiers; there are
 * some blind spots around verifying that e.g. the
 * [io.airbyte.cdk.load.dataflow.aggregate.Aggregate] handles these identifiers correctly.
 *
 * Failure to create a table (e.g. due to syntax error) typically indicates that your
 * [TableSchemaMapper] does not correctly handle certain edge cases, or that your
 * [TableOperationsClient] does not correctly enquote identifiers.
 */
@MicronautTest(environments = ["component"])
interface SchemaMapperSuite {
    val tableSchemaMapper: TableSchemaMapper
    val schemaFactory: TableSchemaFactory
    val opsClient: TableOperationsClient

    val streamFactory: DestinationStreamFactory
    val tableNameResolver: TableNameResolver
    val namespaceMapper: NamespaceMapper

    val reservedKeyword: String
        get() = "table"

    val harness: SchemaMapperHarness
        get() = SchemaMapperHarness(tableSchemaMapper, schemaFactory, opsClient)

    fun `simple table name`(expectedTableName: TableName) {
        harness.testTableIdentifiers("namespace-test", "table-test", expectedTableName)
    }

    fun `funky chars in table name`(expectedTableName: TableName) {
        harness.testTableIdentifiers(
            """namespace-test- -`~!@#$%^&*()-=_+[]\{}|;':",./<>?""",
            """table-test- -`~!@#$%^&*()-=_+[]\{}|;':",./<>?""",
            expectedTableName
        )
    }

    fun `table name starts with non-letter character`(expectedTableName: TableName) {
        harness.testTableIdentifiers("1foo", "1foo", expectedTableName)
    }

    fun `table name is reserved keyword`(expectedTableName: TableName) {
        harness.testTableIdentifiers(reservedKeyword, reservedKeyword, expectedTableName)
    }

    // Intentionally no complex coverage here. We're passing in a pre-munged tablename (i.e should
    // already have special chars, etc. handled).
    fun `simple temp table name`(expectedTableName: TableName) {
        harness.testTempTableIdentifiers("foo", "bar", expectedTableName)
    }

    fun `simple column name`(expectedColumnName: String) {
        harness.testColumnIdentifiers("column-test", expectedColumnName)
    }

    fun `stream names avoid collisions`() {
        val configuredCatalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName("foo-1")
                                    .withNamespace("bar-1")
                                    .withJsonSchema(Jsons.readTree("""{"type": "object"}"""))
                            )
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withSyncId(42)
                            .withMinimumGenerationId(0)
                            .withGenerationId(42),
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName("foo_1")
                                    .withNamespace("bar_1")
                                    .withJsonSchema(Jsons.readTree("""{"type": "object"}"""))
                            )
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withSyncId(42)
                            .withMinimumGenerationId(0)
                            .withGenerationId(42),
                    )
                )
        val syncCatalog =
            DefaultDestinationCatalogFactory()
                .syncCatalog(configuredCatalog, streamFactory, tableNameResolver, namespaceMapper)
        val uniqueFinalTableNames =
            syncCatalog.streams.map { it.tableSchema.tableNames.finalTableName }.toSet()
        assertEquals(
            configuredCatalog.streams.size,
            uniqueFinalTableNames.size,
            "Expected munged table names to be unique: $uniqueFinalTableNames"
        )
    }

    fun `column name with funky chars`(expectedColumnName: String) {
        harness.testColumnIdentifiers(
            """column-test- -`~!@#$%^&*()-=_+[]\{}|;':",./<>?""",
            expectedColumnName
        )
    }

    fun `column name starts with non-letter character`(expectedColumnName: String) {
        harness.testColumnIdentifiers("1foo", expectedColumnName)
    }

    fun `column name is reserved keyword`(expectedColumnName: String) {
        harness.testColumnIdentifiers(reservedKeyword, expectedColumnName)
    }

    fun `column types support all airbyte types`(expectedTypes: Map<String, ColumnType>) = runTest {
        val mappedTypes =
            TableOperationsFixtures.ALL_TYPES_SCHEMA.properties.mapValues { (_, v) ->
                tableSchemaMapper.toColumnType(v)
            }
        assertEquals(expectedTypes, mappedTypes)
        harness.validateCreateTableWithSchema(
            TableOperationsFixtures.ALL_TYPES_SCHEMA.properties,
            mappedTypes,
        )
    }

    fun `column names avoid collisions`() {
        val configuredCatalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName("foo-1")
                                    .withNamespace("bar-1")
                                    .withJsonSchema(
                                        Jsons.readTree(
                                            """
                                            {
                                              "type": "object",
                                              "properties": {
                                                 "foo-1": {"type": "string"},
                                                 "foo_1": {"type": "integer"}
                                              }
                                            }
                                            """.trimIndent()
                                        )
                                    )
                            )
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withSyncId(42)
                            .withMinimumGenerationId(0)
                            .withGenerationId(42),
                    )
                )
        val syncCatalog =
            DefaultDestinationCatalogFactory()
                .syncCatalog(configuredCatalog, streamFactory, tableNameResolver, namespaceMapper)
        val uniqueColumnNames =
            syncCatalog.streams.first().tableSchema.columnSchema.finalSchema.keys
        assertEquals(
            configuredCatalog.streams.first().stream.jsonSchema["properties"].size(),
            uniqueColumnNames.size,
            "Expected munged column names to be unique: $uniqueColumnNames"
        )
    }

    companion object {
        val intType = FieldType(IntegerType, nullable = true)
    }
}
