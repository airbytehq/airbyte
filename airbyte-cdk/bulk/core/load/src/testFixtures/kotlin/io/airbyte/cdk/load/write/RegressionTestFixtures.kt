/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.test.util.CharacterizationTest
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.SchemaDumper
import io.airbyte.cdk.load.test.util.destination_process.DestinationProcessFactory
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest.Companion.numberType
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.assertAll

class RegressionTestFixtures(
    val schemaDumperProvider: ((ConfigurationSpecification) -> SchemaDumper)?,
    val opsClientProvider: ((ConfigurationSpecification) -> TableOperationsClient)?,
    val destinationProcessFactory: DestinationProcessFactory,
    val updatedConfig: String,
    val parsedConfig: ConfigurationSpecification,
    val goldenFileBasePath: String,
    val testPrettyName: String,
    val tableIdentifierRegressionTestExpectedTableNames: List<TableName>,
) {
    // hardcode these values.
    // these tests only depend on the catalog, which is identical between speed and normal mode.
    // so there's no point making this configurable.
    val dataChannelMedium = DataChannelMedium.STDIO
    val dataChannelFormat = DataChannelFormat.JSONL
    val randomizedNamespace = IntegrationTest.generateRandomNamespace()

    fun baseSchemaRegressionTest(filename: String, importType: ImportType) = runTest {
        assumeTrue(schemaDumperProvider != null)
        val schemaDumper = schemaDumperProvider!!(parsedConfig)
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                importType,
                ObjectType(
                    linkedMapOf(
                        // Validate every airbyte type
                        "string" to FieldType(StringType, nullable = true),
                        "number" to FieldType(NumberType, nullable = true),
                        "integer" to FieldType(IntegerType, nullable = true),
                        "boolean" to FieldType(BooleanType, nullable = true),
                        "timestamp_with_timezone" to
                            FieldType(TimestampTypeWithTimezone, nullable = true),
                        "timestamp_without_timezone" to
                            FieldType(TimestampTypeWithoutTimezone, nullable = true),
                        "time_with_timezone" to FieldType(TimeTypeWithTimezone, nullable = true),
                        "time_without_timezone" to
                            FieldType(TimeTypeWithoutTimezone, nullable = true),
                        "date" to FieldType(DateType, nullable = true),
                        "object" to
                            FieldType(
                                ObjectType(linkedMapOf("foo" to numberType)),
                                nullable = true
                            ),
                        "object_with_empty_schema" to
                            FieldType(ObjectTypeWithEmptySchema, nullable = true),
                        "object_without_schema" to
                            FieldType(ObjectTypeWithoutSchema, nullable = true),
                        "array" to FieldType(ArrayType(numberType), nullable = true),
                        "array_without_schema" to
                            FieldType(ArrayTypeWithoutSchema, nullable = true),
                        "union" to
                            FieldType(
                                UnionType.of(
                                    listOf(IntegerType, ObjectTypeWithoutSchema),
                                    isLegacyUnion = false
                                ),
                                nullable = true
                            ),
                        "legacy_union" to
                            FieldType(
                                UnionType.of(
                                    listOf(IntegerType, ObjectTypeWithoutSchema),
                                    isLegacyUnion = false
                                ),
                                nullable = true
                            ),
                        "unknown" to
                            FieldType(
                                UnknownType(Jsons.readTree("""{"type":"potato"}""")),
                                nullable = true
                            ),
                        // and their nonnull equivalents
                        "string_nonnull" to FieldType(StringType, nullable = false),
                        "number_nonnull" to FieldType(NumberType, nullable = false),
                        "integer_nonnull" to FieldType(IntegerType, nullable = false),
                        "boolean_nonnull" to FieldType(BooleanType, nullable = false),
                        "timestamp_with_timezone_nonnull" to
                            FieldType(TimestampTypeWithTimezone, nullable = false),
                        "timestamp_without_timezone_nonnull" to
                            FieldType(TimestampTypeWithoutTimezone, nullable = false),
                        "time_with_timezone_nonnull" to
                            FieldType(TimeTypeWithTimezone, nullable = false),
                        "time_without_timezone_nonnull" to
                            FieldType(TimeTypeWithoutTimezone, nullable = false),
                        "date_nonnull" to FieldType(DateType, nullable = false),
                        "object_nonnull" to
                            FieldType(
                                ObjectType(linkedMapOf("foo" to numberType)),
                                nullable = false
                            ),
                        "object_with_empty_schema_nonnull" to
                            FieldType(ObjectTypeWithEmptySchema, nullable = false),
                        "object_without_schema_nonnull" to
                            FieldType(ObjectTypeWithoutSchema, nullable = false),
                        "array_nonnull" to FieldType(ArrayType(numberType), nullable = false),
                        "array_without_schema_nonnull" to
                            FieldType(ArrayTypeWithoutSchema, nullable = false),
                        "union_nonnull" to
                            FieldType(
                                UnionType.of(
                                    listOf(IntegerType, ObjectTypeWithoutSchema),
                                    isLegacyUnion = false
                                ),
                                nullable = false
                            ),
                        "legacy_union_nonnull" to
                            FieldType(
                                UnionType.of(
                                    listOf(IntegerType, ObjectTypeWithoutSchema),
                                    isLegacyUnion = false
                                ),
                                nullable = false
                            ),
                        "unknown_nonnull" to
                            FieldType(
                                UnknownType(Jsons.readTree("""{"type":"potato"}""")),
                                nullable = false
                            ),
                        // and some interesting identifiers:
                        // common SQL reserved words
                        "table" to FieldType(StringType, nullable = true),
                        "column" to FieldType(StringType, nullable = true),
                        "create" to FieldType(StringType, nullable = true),
                        "delete" to FieldType(StringType, nullable = true),
                        // funky chars
                        FUNKY_CHARS_IDENTIFIER to FieldType(StringType, nullable = true),
                        // starts with a number
                        "1column" to FieldType(StringType, nullable = true),
                        // column names that probably collide
                        "foo!" to FieldType(StringType, nullable = true),
                        "foo$" to FieldType(StringType, nullable = true),
                        "foo_" to FieldType(StringType, nullable = true),
                        // upper/lowercasing
                        "UPPER_CASE" to FieldType(StringType, nullable = true),
                        "Mixed_Case" to FieldType(StringType, nullable = true),
                    )
                ),
                generationId = 1,
                minimumGenerationId = 1,
                syncId = 42,
                namespaceMapper = dataChannelMedium.namespaceMapper(),
                tableSchema = BasicFunctionalityIntegrationTest.emptyTableSchema,
            )
        destinationProcessFactory.runSync(
            updatedConfig,
            DestinationCatalog(listOf(stream)),
            messages = emptyList(),
            testPrettyName,
            dataChannelMedium,
            dataChannelFormat,
        )

        val actualSchema =
            Jsons.writerWithDefaultPrettyPrinter()
                .writeValueAsString(
                    schemaDumper.discoverSchema(
                        stream.mappedDescriptor.namespace,
                        stream.mappedDescriptor.name
                    )
                )
        CharacterizationTest.doAssert(
            "$goldenFileBasePath/schema-regression/column_names/$filename.json",
            actualSchema,
        )
    }

    fun baseTableIdentifierRegressionTest(importType: ImportType) = runTest {
        assumeTrue(opsClientProvider != null)
        assertEquals(
            tableIdentifierRegressionInputStreamDescriptors.size,
            tableIdentifierRegressionTestExpectedTableNames.size,
            "tableIdentifierRegressionTestExpectedTableNames has incorrect length; did you miss some test cases?",
        )
        val opsClient = opsClientProvider!!(parsedConfig)
        tableIdentifierRegressionTestExpectedTableNames.forEach {
            if (opsClient.tableExists(it)) {
                opsClient.dropTable(it)
            }
        }
        val catalog =
            DestinationCatalog(
                tableIdentifierRegressionInputStreamDescriptors.map { (inputNamespace, inputName) ->
                    DestinationStream(
                        inputNamespace,
                        inputName,
                        importType,
                        ObjectType(linkedMapOf("blah" to FieldType(StringType, nullable = true))),
                        generationId = 1,
                        minimumGenerationId = 1,
                        syncId = 42,
                        namespaceMapper = dataChannelMedium.namespaceMapper(),
                        tableSchema = BasicFunctionalityIntegrationTest.emptyTableSchema,
                    )
                }
            )
        assertDoesNotThrow {
            destinationProcessFactory.runSync(
                updatedConfig,
                catalog,
                messages = emptyList(),
                testPrettyName,
                dataChannelMedium,
                dataChannelFormat,
            )
        }
        val assertions: Array<() -> Unit> =
            tableIdentifierRegressionTestExpectedTableNames
                .map {
                    // map each expected TableName to a lambda that asserts that the table exists
                    {
                        runBlocking {
                            assertTrue(
                                opsClient.tableExists(it),
                                "Expected table ${it.toPrettyString()} to exist"
                            )
                        }
                    }
                }
                .toTypedArray()
        assertAll(*assertions)
    }

    companion object {
        const val FUNKY_CHARS_IDENTIFIER = "é,./<>?'\";[]\\:{}|`~!@#$%^&*()_+-="
        val tableIdentifierRegressionInputStreamDescriptors =
            listOf(
                // basic identifier
                DestinationStream.Descriptor(
                    "table_id_regression_test",
                    "table_id_regression_test"
                ),
                // some reserved words
                DestinationStream.Descriptor("table", "table"),
                DestinationStream.Descriptor("column", "column"),
                DestinationStream.Descriptor("create", "create"),
                DestinationStream.Descriptor("delete", "delete"),
                // funky char
                DestinationStream.Descriptor(FUNKY_CHARS_IDENTIFIER, FUNKY_CHARS_IDENTIFIER),
                // starts with a number
                DestinationStream.Descriptor("1foo", "1foo"),
                // namespaces that probably collide
                DestinationStream.Descriptor("foo!", "table_id_regression_test"),
                DestinationStream.Descriptor("foo$", "table_id_regression_test"),
                DestinationStream.Descriptor("foo_", "table_id_regression_test"),
                // names that probably collide
                DestinationStream.Descriptor("table_id_regression_test", "foo!"),
                DestinationStream.Descriptor("table_id_regression_test", "foo$"),
                DestinationStream.Descriptor("table_id_regression_test", "foo_"),
                // upper/lowercasing
                DestinationStream.Descriptor("UPPER_CASE", "UPPER_CASE"),
                DestinationStream.Descriptor("Mixed_Case", "Mixed_Case"),
            )
    }
}
