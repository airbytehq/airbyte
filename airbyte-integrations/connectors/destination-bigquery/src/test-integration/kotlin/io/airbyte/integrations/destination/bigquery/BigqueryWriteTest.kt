/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.test.util.destination_process.DestinationUncleanExitException
import io.airbyte.cdk.load.test.util.destination_process.DockerizedDestinationFactory
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
import org.junit.jupiter.api.assertThrows

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
    private val typingDedupingDestinationFactory =
        DockerizedDestinationFactory("airbyte/destination-bigquery", "2.11.4")
    @Test
    open fun testTempTableMigration() {
        fun makeStream(genId: Long, minGenId: Long): DestinationStream {
            return DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = genId,
                minimumGenerationId = minGenId,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
            )
        }
        // Populate a table using the T+D destination
        val originalSyncStream = makeStream(genId = 5, minGenId = 0)
        runSync(
            updatedConfig,
            originalSyncStream,
            listOf(
                InputRecord(
                    originalSyncStream,
                    data = """{"id": 1}""",
                    emittedAtMs = 1,
                ),
            ),
            destinationProcessFactory = typingDedupingDestinationFactory,
        )
        // Start a truncate refresh on the T+D destination,
        // but send an INCOMPLETE status so that it fails.
        // This will create a temp table containing the `id=2` record.
        val truncateSyncStream = makeStream(genId = 6, minGenId = 6)
        assertThrows<DestinationUncleanExitException> {
            runSync(
                updatedConfig,
                truncateSyncStream,
                listOf(
                    InputRecord(
                        truncateSyncStream,
                        data = """{"id": 2}""",
                        emittedAtMs = 2,
                    ),
                ),
                streamStatus = null,
                destinationProcessFactory = typingDedupingDestinationFactory,
            )
        }
        // Finish the truncate refresh using the current destination.
        // We should correctly retain the `id=2` record.
        runSync(
            updatedConfig,
            truncateSyncStream,
            listOf(
                InputRecord(
                    truncateSyncStream,
                    data = """{"id": 3}""",
                    emittedAtMs = 3,
                ),
            ),
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                // id = 1 was deleted, id = 2 and 3 were retained
                OutputRecord(
                    extractedAt = 2,
                    generationId = 6,
                    data = mapOf("id" to 2),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 3,
                    generationId = 6,
                    data = mapOf("id" to 3),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
            ),
            truncateSyncStream,
            primaryKey = listOf(listOf("id")),
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
    )

class StandardInsertRawOverride :
    BigqueryDirectLoadWriteTest(
        BigQueryDestinationTestUtils.standardInsertRawOverrideConfig,
        CdcDeletionMode.HARD_DELETE,
    )

class StandardInsert :
    BigqueryDirectLoadWriteTest(
        BigQueryDestinationTestUtils.standardInsertConfig,
        CdcDeletionMode.HARD_DELETE,
    )

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
    )

class GcsRawOverride :
    BigqueryDirectLoadWriteTest(
        BigQueryDestinationTestUtils.createConfig(
            configFile = GCS_STAGING_CONFIG,
            rawDatasetId = RAW_DATASET_OVERRIDE,
        ),
        CdcDeletionMode.HARD_DELETE,
    )

class Gcs :
    BigqueryDirectLoadWriteTest(
        BigQueryDestinationTestUtils.createConfig(configFile = GCS_STAGING_CONFIG),
        CdcDeletionMode.HARD_DELETE,
    )
