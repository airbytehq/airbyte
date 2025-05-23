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
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.toolkits.load.db.orchestration.ColumnNameModifyingMapper
import io.airbyte.cdk.load.toolkits.load.db.orchestration.RootLevelTimestampsToUtcMapper
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
import io.airbyte.integrations.destination.bigquery.spec.CdcDeletionMode
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigqueryColumnNameGenerator
import org.junit.jupiter.api.Test

abstract class BigqueryWriteTest(
    configContents: String,
    dataDumper: DestinationDataDumper,
    expectedRecordMapper: ExpectedRecordMapper,
    isStreamSchemaRetroactive: Boolean,
    preserveUndeclaredFields: Boolean,
    commitDataIncrementallyToEmptyDestination: Boolean,
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
        commitDataIncrementallyToEmptyDestination = commitDataIncrementallyToEmptyDestination,
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
        commitDataIncrementallyToEmptyDestination = false,
        dedupBehavior = null,
        nullEqualsUnset = false,
        Untyped,
    )

abstract class BigqueryDirectLoadWriteTest(
    configContents: String,
    cdcDeletionMode: CdcDeletionMode,
) :
    BigqueryWriteTest(
        configContents = configContents,
        BigqueryFinalTableDataDumper,
        ColumnNameModifyingMapper(BigqueryColumnNameGenerator())
            .compose(TimeWithTimezoneMapper)
            .compose(RootLevelTimestampsToUtcMapper)
            .compose(IntegralNumberRecordMapper),
        isStreamSchemaRetroactive = true,
        preserveUndeclaredFields = false,
        commitDataIncrementallyToEmptyDestination = true,
        dedupBehavior =
            DedupBehavior(
                cdcDeletionMode =
                    when (cdcDeletionMode) {
                        // medium confidence: the CDK might eventually add other deletion modes,
                        // which this destination won't immediately support,
                        // so we should have separate enums.
                        // otherwise the new enum values would show up in the spec, which we don't
                        // want.
                        CdcDeletionMode.HARD_DELETE ->
                            io.airbyte.cdk.load.write.DedupBehavior.CdcDeletionMode.HARD_DELETE
                        CdcDeletionMode.SOFT_DELETE ->
                            io.airbyte.cdk.load.write.DedupBehavior.CdcDeletionMode.SOFT_DELETE
                    }
            ),
        nullEqualsUnset = true,
        StronglyTyped(
            convertAllValuesToString = true,
            topLevelFloatLosesPrecision = true,
            nestedFloatLosesPrecision = true,
            integerCanBeLarge = false,
            numberCanBeLarge = false,
            timeWithTimezoneBehavior = SimpleValueBehavior.STRONGLY_TYPE,
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

class StandardInsertRawOverrideRawTables :
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
    BigqueryDirectLoadWriteTest(
        BigQueryDestinationTestUtils.standardInsertRawOverrideConfig,
        CdcDeletionMode.HARD_DELETE,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
    @Test
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }
}

class StandardInsert :
    BigqueryDirectLoadWriteTest(
        BigQueryDestinationTestUtils.standardInsertConfig,
        CdcDeletionMode.HARD_DELETE,
    ) {
    @Test
    override fun testAppendJsonSchemaEvolution() {
        super.testAppendJsonSchemaEvolution()
    }
}

class StandardInsertCdcSoftDeletes :
    BigqueryDirectLoadWriteTest(
        BigQueryDestinationTestUtils.createConfig(
            configFile = STANDARD_INSERT_CONFIG,
            cdcDeletionMode = CdcDeletionMode.SOFT_DELETE,
        ),
        CdcDeletionMode.SOFT_DELETE
    ) {
    @Test
    override fun testDedup() {
        super.testDedup()
    }
}

class GcsRawOverrideRawTables :
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
    BigqueryDirectLoadWriteTest(
        BigQueryDestinationTestUtils.createConfig(
            configFile = GCS_STAGING_CONFIG,
            rawDatasetId = RAW_DATASET_OVERRIDE,
        ),
        CdcDeletionMode.HARD_DELETE,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

class Gcs :
    BigqueryDirectLoadWriteTest(
        BigQueryDestinationTestUtils.createConfig(configFile = GCS_STAGING_CONFIG),
        CdcDeletionMode.HARD_DELETE,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}
