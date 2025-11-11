/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.write.*
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeSpecification
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

@Execution(ExecutionMode.SAME_THREAD)
@Disabled("Tests doesnt work in CI")
class GcsPolarisWriteTest :
    BasicFunctionalityIntegrationTest(
        configContents = getConfig(),
        configSpecClass = GcsDataLakeSpecification::class.java,
        dataDumper =
            BigLakeDataDumper(
                delegateDataDumper =
                    io.airbyte.cdk.load.data.icerberg.parquet.IcebergDataDumper(
                        tableIdGenerator = SimpleTableIdGenerator(),
                        getCatalog = { spec ->
                            GcsDataLakeTestUtil.getCatalog(GcsDataLakeTestUtil.getConfig(spec))
                        }
                    )
            ),
        destinationCleaner = NoopDestinationCleaner,
        recordMangler = io.airbyte.cdk.load.data.icerberg.parquet.IcebergExpectedRecordMapper,
        isStreamSchemaRetroactive = true,
        isStreamSchemaRetroactiveForUnknownTypeToString = false,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.SOFT_DELETE),
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.STRINGIFY,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        allTypesBehavior =
            StronglyTyped(integerCanBeLarge = false, nestedFloatLosesPrecision = false),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
        nullEqualsUnset = true,
        configUpdater = io.airbyte.cdk.load.data.icerberg.parquet.IcebergConfigUpdater,
        useDataFlowPipeline = true
    ) {

    @Test
    @Disabled("https://github.com/airbytehq/airbyte-internal-issues/issues/11439")
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }

    @Test
    override fun testAppendSchemaEvolution() {
        assumeTrue(verifyDataWriting)
        fun makeStream(syncId: Long, schema: LinkedHashMap<String, FieldType>) =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream",
                Append,
                ObjectType(schema),
                generationId = 0,
                minimumGenerationId = 0,
                syncId,
                namespaceMapper = NamespaceMapper()
            )
        val firstStream =
            makeStream(
                syncId = 42,
                linkedMapOf("id" to intType, "to_drop" to stringType, "same" to intType)
            )
        runSync(
            updatedConfig,
            firstStream,
            listOf(
                InputRecord(
                    firstStream,
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
                    finalStream,
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

    companion object {
        fun getConfig(): String = PolarisEnvironment.getConfig()

        @JvmStatic
        @BeforeAll
        fun setup() {
            PolarisEnvironment.startServices()
        }

        @JvmStatic
        @AfterAll
        fun stop() {
            PolarisEnvironment.stopServices()
        }
    }
}
