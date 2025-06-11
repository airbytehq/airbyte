/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
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
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import java.time.LocalDate
import org.junit.jupiter.api.Assumptions.assumeTrue
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
    ) {
        @Test
        fun testValidDatetimeRanges() {
            assumeTrue(verifyDataWriting)
            val stream =
                DestinationStream(
                    unmappedNamespace = randomizedNamespace,
                    unmappedName = "test_stream",
                    Append,
                    ObjectType(
                        linkedMapOf(
                            "timestamp_with_timezone" to
                                FieldType(TimestampTypeWithTimezone, nullable = true),
                            "timestamp_without_timezone" to
                                FieldType(TimestampTypeWithoutTimezone, nullable = true),
                            "time_with_timezone" to FieldType(TimeTypeWithTimezone, nullable = true),
                            "time_without_timezone" to
                                FieldType(TimeTypeWithoutTimezone, nullable = true),
                            "date" to FieldType(DateType, nullable = true),
                        )
                    ),
                    generationId = 42,
                    minimumGenerationId = 0,
                    syncId = 42,
                    namespaceMapper = namespaceMapperForMedium()
                )

            runSync(
                updatedConfig,
                stream,
                listOf(
                    InputRecord(
                        stream,
                        """
                        {
                          "timestamp_without_timezone": ${LocalDate.parse("19999-12-31")}
                        }
                    """.trimIndent(),
                        emittedAtMs = 100,
                    )
                )
            )

            dumpAndDiffRecords(
                parsedConfig,
                listOf(
                    OutputRecord(
                        extractedAt = 100,
                        generationId = 42,
                        data = mapOf("timestamp_without_timezone" to listOf(42.0, null)),
                        airbyteMeta =
                            OutputRecord.Meta(
                                syncId = 42,
                                changes =
                                    listOf(
                                        Meta.Change(
                                            "array.1",
                                            Change.NULLED,
                                            Reason.DESTINATION_SERIALIZATION_ERROR
                                        )
                                    )
                            ),
                    ),
                ),
                stream,
                primaryKey = listOf(listOf("id")),
                cursor = null,
            )
        }
    }

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
    )

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
