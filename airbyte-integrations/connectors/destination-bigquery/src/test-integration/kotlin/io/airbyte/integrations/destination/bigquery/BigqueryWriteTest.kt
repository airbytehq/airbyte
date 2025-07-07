/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

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
    commitDataIncrementallyToEmptyDestinationOnAppend: Boolean,
    dedupBehavior: DedupBehavior?,
    nullEqualsUnset: Boolean,
    allTypesBehavior: AllTypesBehavior,
    coercesLegacyUnions: Boolean,
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
        coercesLegacyUnions = coercesLegacyUnions,
        preserveUndeclaredFields = preserveUndeclaredFields,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        commitDataIncrementallyToEmptyDestinationOnAppend =
            commitDataIncrementallyToEmptyDestinationOnAppend,
        commitDataIncrementallyToEmptyDestinationOnDedupe = false,
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
        commitDataIncrementallyToEmptyDestinationOnAppend = false,
        dedupBehavior = null,
        nullEqualsUnset = false,
        Untyped,
        coercesLegacyUnions = false,
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
        commitDataIncrementallyToEmptyDestinationOnAppend = true,
        dedupBehavior =
            DedupBehavior(
                cdcDeletionMode =
                    when (cdcDeletionMode) {
                        // medium confidence: the CDK might eventually add other deletion modes,
                        // which this destination won't immediately support,
                        // so we should have separate enums.
                        // otherwise the new enum values would show up in the spec, which we don't
                        // want.
                        CdcDeletionMode.HARD_DELETE -> DedupBehavior.CdcDeletionMode.HARD_DELETE
                        CdcDeletionMode.SOFT_DELETE -> DedupBehavior.CdcDeletionMode.SOFT_DELETE
                    }
            ),
        nullEqualsUnset = true,
        StronglyTyped(
            convertAllValuesToString = true,
            topLevelFloatLosesPrecision = true,
            nestedFloatLosesPrecision = true,
            integerCanBeLarge = false,
            numberCanBeLarge = false,
            numberIsFixedPointPrecision38Scale9 = true,
            timeWithTimezoneBehavior = SimpleValueBehavior.STRONGLY_TYPE,
        ),
        coercesLegacyUnions = true,
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
