/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.icerberg.parquet

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.BaseDeltaTaskWriter
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import kotlin.test.assertContains
import org.apache.iceberg.catalog.Catalog
import org.junit.jupiter.api.Assumptions
import org.junit.jupiter.api.Test

abstract class IcebergWriteTest(
    configContents: String,
    configSpecClass: Class<out ConfigurationSpecification>,
    getCatalog: (ConfigurationSpecification) -> Catalog,
    destinationCleaner: DestinationCleaner,
    tableIdGenerator: TableIdGenerator,
    additionalMicronautEnvs: List<String> = emptyList(),
    micronautProperties: Map<Property, String> = emptyMap(),
) :
    BasicFunctionalityIntegrationTest(
        configContents,
        configSpecClass,
        IcebergDataDumper(tableIdGenerator, getCatalog),
        destinationCleaner,
        IcebergExpectedRecordMapper,
        additionalMicronautEnvs = additionalMicronautEnvs,
        micronautProperties = micronautProperties,
        isStreamSchemaRetroactive = true,
        supportsDedup = true,
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.STRINGIFY,
        preserveUndeclaredFields = false,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false,
                // we stringify objects, so nested floats stay exact
                nestedFloatLosesPrecision = false
            ),
        nullUnknownTypes = true,
        nullEqualsUnset = true,
        configUpdater = IcebergConfigUpdater,
    ) {
    /**
     * This test differs from the base test in two critical aspects:
     *
     * 1. Data Type Conversion:
     * ```
     *    The base test attempts to change a column's data type from INTEGER to STRING,
     *    which Iceberg does not support and will throw an exception.
     * ```
     * 2. Result Ordering:
     * ```
     *    While the data content matches exactly, Iceberg returns results in a different
     *    order than what the base test expects. The base test's ordering assumptions
     *    need to be adjusted accordingly.
     * ```
     */
    @Test
    override fun testAppendSchemaEvolution() {
        Assumptions.assumeTrue(verifyDataWriting)
        fun makeStream(syncId: Long, schema: LinkedHashMap<String, FieldType>) =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                Append,
                ObjectType(schema),
                generationId = 0,
                minimumGenerationId = 0,
                syncId,
            )
        runSync(
            updatedConfig,
            makeStream(
                syncId = 42,
                linkedMapOf("id" to intType, "to_drop" to stringType, "same" to intType)
            ),
            listOf(
                InputRecord(
                    randomizedNamespace,
                    "test_stream",
                    """{"id": 42, "to_drop": "val1", "same": 42}""",
                    emittedAtMs = 1234L,
                )
            )
        )
        val finalStream =
            makeStream(
                syncId = 43,
                linkedMapOf("id" to intType, "same" to intType, "to_add" to stringType)
            )
        runSync(
            updatedConfig,
            finalStream,
            listOf(
                InputRecord(
                    randomizedNamespace,
                    "test_stream",
                    """{"id": 42, "same": "43", "to_add": "val3"}""",
                    emittedAtMs = 1234,
                )
            )
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data = mapOf("id" to 42, "same" to 42),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data = mapOf("id" to 42, "same" to 43, "to_add" to "val3"),
                    airbyteMeta = OutputRecord.Meta(syncId = 43),
                )
            ),
            finalStream,
            primaryKey = listOf(listOf("id")),
            cursor = listOf("same"),
        )
    }

    /**
     * Iceberg disallows null values in identifier columns. In dedup mode, we set the PK columns to
     * be Iceberg identifier columns. Therefore, we should detect null values in PK columns, and
     * throw them as a ConfigError.
     */
    @Test
    open fun testDedupNullPk() {
        val failure = expectFailure {
            runSync(
                updatedConfig,
                DestinationStream(
                    DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                    Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList()),
                    ObjectType(linkedMapOf("id" to FieldType(IntegerType, nullable = true))),
                    generationId = 42,
                    minimumGenerationId = 0,
                    syncId = 12,
                ),
                listOf(
                    InputRecord(
                        randomizedNamespace,
                        "test_stream",
                        """{"id": null}""",
                        emittedAtMs = 1234L,
                    )
                )
            )
        }
        assertContains(
            failure.message,
            BaseDeltaTaskWriter.NULL_PK_ERROR_MESSAGE,
        )
    }
}
