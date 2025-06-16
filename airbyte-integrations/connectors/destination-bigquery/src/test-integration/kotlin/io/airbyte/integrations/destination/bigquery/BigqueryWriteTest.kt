/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.test.util.destination_process.DockerizedDestinationFactory
import io.airbyte.cdk.load.toolkits.load.db.orchestration.ColumnNameModifyingMapper
import io.airbyte.cdk.load.toolkits.load.db.orchestration.RootLevelTimestampsToUtcMapper
import io.airbyte.cdk.load.toolkits.load.db.orchestration.TypingDedupingMetaChangeMapper
import io.airbyte.cdk.load.write.AllTypesBehavior
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.SimpleValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import io.airbyte.integrations.destination.bigquery.BigQueryDestinationTestUtils.GCS_STAGING_CONFIG
import io.airbyte.integrations.destination.bigquery.BigQueryDestinationTestUtils.RAW_DATASET_OVERRIDE
import io.airbyte.integrations.destination.bigquery.BigQueryDestinationTestUtils.STANDARD_INSERT_CONFIG
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigqueryColumnNameGenerator
import kotlin.test.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

abstract class BigqueryWriteTest(
    configContents: String,
    dataDumper: DestinationDataDumper,
    expectedRecordMapper: ExpectedRecordMapper,
    isStreamSchemaRetroactive: Boolean,
    preserveUndeclaredFields: Boolean,
    dedupBehavior: DedupBehavior?,
    nullEqualsUnset: Boolean,
    allTypesBehavior: AllTypesBehavior,
) :
    BasicFunctionalityIntegrationTest(
        configContents = configContents,
        BigquerySpecification::class.java,
        dataDumper,
        BigqueryDestinationCleaner,
        recordMangler = expectedRecordMapper,
        isStreamSchemaRetroactive = isStreamSchemaRetroactive,
        dedupBehavior = dedupBehavior,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        preserveUndeclaredFields = preserveUndeclaredFields,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        allTypesBehavior = allTypesBehavior,
        nullEqualsUnset = nullEqualsUnset,
        configUpdater = BigqueryConfigUpdater,
        additionalMicronautEnvs = additionalMicronautEnvs,
    )

abstract class BigqueryRawTablesWriteTest(
    configContents: String,
) :
    BigqueryWriteTest(
        configContents = configContents,
        BigqueryRawTableDataDumper,
        UncoercedExpectedRecordMapper,
        isStreamSchemaRetroactive = false,
        preserveUndeclaredFields = true,
        dedupBehavior = null,
        nullEqualsUnset = false,
        Untyped,
    )

abstract class BigqueryTDWriteTest(configContents: String) :
    BigqueryWriteTest(
        configContents = configContents,
        BigqueryFinalTableDataDumper,
        ColumnNameModifyingMapper(BigqueryColumnNameGenerator())
            .compose(RootLevelTimestampsToUtcMapper)
            .compose(TypingDedupingMetaChangeMapper)
            .compose(IntegralNumberRecordMapper),
        isStreamSchemaRetroactive = true,
        preserveUndeclaredFields = false,
        dedupBehavior = DedupBehavior(),
        nullEqualsUnset = true,
        StronglyTyped(
            convertAllValuesToString = true,
            topLevelFloatLosesPrecision = true,
            nestedFloatLosesPrecision = true,
            integerCanBeLarge = false,
            numberCanBeLarge = false,
            timeWithTimezoneBehavior = SimpleValueBehavior.PASS_THROUGH,
        ),
    ) {
    private val oldCdkDestinationFactory =
        DockerizedDestinationFactory("airbyte/destination-bigquery", "2.10.2")

    @Test
    open fun testAppendCdkMigration() {
        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = NamespaceMapper()
            )
        // Run a sync on the old CDK
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    data = """{"id": 1234}""",
                    emittedAtMs = 1234,
                ),
            ),
            destinationProcessFactory = oldCdkDestinationFactory,
        )
        // Grab the loaded_at value from this sync
        val firstSyncLoadedAt =
            BigqueryRawTableDataDumper.dumpRecords(parsedConfig, stream).first().loadedAt!!

        // Run a sync with the current destination
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    data = """{"id": 1234}""",
                    emittedAtMs = 5678,
                ),
            ),
        )
        val secondSyncLoadedAt =
            BigqueryRawTableDataDumper.dumpRecords(parsedConfig, stream)
                .map { it.loadedAt!! }
                .toSet()
        // verify that we didn't execute a soft reset
        assertAll(
            {
                assertEquals(
                    2,
                    secondSyncLoadedAt.size,
                    "Expected two unique values for loaded_at after two syncs. If there is only 1 value, then we likely executed a soft reset.",
                )
            },
            {
                assertTrue(
                    secondSyncLoadedAt.contains(firstSyncLoadedAt),
                    "Expected the first sync's loaded_at value to exist after the second sync. If this is not true, then we likely executed a soft reset.",
                )
            },
        )

        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data = mapOf("id" to 1234),
                    airbyteMeta = OutputRecord.Meta(syncId = 42, changes = emptyList()),
                ),
                OutputRecord(
                    extractedAt = 5678,
                    generationId = 0,
                    data = mapOf("id" to 1234),
                    airbyteMeta = OutputRecord.Meta(syncId = 42, changes = emptyList()),
                ),
            ),
            stream,
            listOf(listOf("id")),
            cursor = null,
        )
    }

    @Test
    open fun testDedupCdkMigration() {
        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream",
                Dedupe(primaryKey = listOf(listOf("id")), cursor = emptyList()),
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = NamespaceMapper(),
            )
        // Run a sync on the old CDK
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    data = """{"id": 1234}""",
                    emittedAtMs = 1234,
                ),
            ),
            destinationProcessFactory = oldCdkDestinationFactory,
        )
        // Grab the loaded_at value from this sync
        val firstSyncLoadedAt =
            BigqueryRawTableDataDumper.dumpRecords(parsedConfig, stream).first().loadedAt!!

        // Run a sync with the current destination
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream = stream,
                    data = """{"id": 1234}""",
                    emittedAtMs = 5678,
                ),
            ),
        )
        val secondSyncLoadedAt =
            BigqueryRawTableDataDumper.dumpRecords(parsedConfig, stream)
                .map { it.loadedAt!! }
                .toSet()
        // verify that we didn't execute a soft reset
        assertAll(
            {
                assertEquals(
                    2,
                    secondSyncLoadedAt.size,
                    "Expected two unique values for loaded_at after two syncs. If there is only 1 value, then we likely executed a soft reset.",
                )
            },
            {
                assertTrue(
                    secondSyncLoadedAt.contains(firstSyncLoadedAt),
                    "Expected the first sync's loaded_at value to exist after the second sync. If this is not true, then we likely executed a soft reset.",
                )
            },
        )

        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 5678,
                    generationId = 0,
                    data = mapOf("id" to 1234),
                    airbyteMeta = OutputRecord.Meta(syncId = 42, changes = emptyList()),
                ),
            ),
            stream,
            listOf(listOf("id")),
            cursor = null,
        )
    }
}

class StandardInsertRawOverrideDisableTd :
    BigqueryRawTablesWriteTest(
        BigQueryDestinationTestUtils.createConfig(
            configFile = STANDARD_INSERT_CONFIG,
            rawDatasetId = RAW_DATASET_OVERRIDE,
            disableTypingDeduping = true,
        ),
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }
}

class StandardInsertRawOverride :
    BigqueryTDWriteTest(BigQueryDestinationTestUtils.standardInsertRawOverrideConfig) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
    @Test
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }
}

class StandardInsert : BigqueryTDWriteTest(BigQueryDestinationTestUtils.standardInsertConfig) {
    @Test
    override fun testDedup() {
        super.testDedup()
    }
}

class GcsRawOverrideDisableTd :
    BigqueryRawTablesWriteTest(
        BigQueryDestinationTestUtils.createConfig(
            configFile = GCS_STAGING_CONFIG,
            rawDatasetId = RAW_DATASET_OVERRIDE,
            disableTypingDeduping = true,
        ),
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

class GcsRawOverride :
    BigqueryTDWriteTest(
        BigQueryDestinationTestUtils.createConfig(
            configFile = GCS_STAGING_CONFIG,
            rawDatasetId = RAW_DATASET_OVERRIDE,
        ),
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

class Gcs :
    BigqueryTDWriteTest(
        BigQueryDestinationTestUtils.createConfig(configFile = GCS_STAGING_CONFIG)
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}
