/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.toolkits.load.db.orchestration.ColumnNameModifyingMapper
import io.airbyte.cdk.load.toolkits.load.db.orchestration.RootLevelTimestampsToUtcMapper
import io.airbyte.cdk.load.toolkits.load.db.orchestration.TypingDedupingMetaChangeMapper
import io.airbyte.cdk.load.write.AllTypesBehavior
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.SimpleValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import io.airbyte.integrations.destination.bigquery.BigQueryDestinationTestUtils.GCS_STAGING_CONFIG
import io.airbyte.integrations.destination.bigquery.BigQueryDestinationTestUtils.RAW_DATASET_OVERRIDE
import io.airbyte.integrations.destination.bigquery.BigQueryDestinationTestUtils.STANDARD_INSERT_CONFIG
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigqueryColumnNameGenerator
import org.junit.jupiter.api.Test

abstract class BigqueryWriteTest(
    configContents: String,
    dataDumper: DestinationDataDumper,
    expectedRecordMapper: ExpectedRecordMapper,
    isStreamSchemaRetroactive: Boolean,
    preserveUndeclaredFields: Boolean,
    supportsDedup: Boolean,
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
        supportsDedup = supportsDedup,
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
        supportsDedup = false,
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
        supportsDedup = true,
        nullEqualsUnset = true,
        StronglyTyped(
            convertAllValuesToString = true,
            topLevelFloatLosesPrecision = true,
            nestedFloatLosesPrecision = true,
            integerCanBeLarge = false,
            numberCanBeLarge = false,
            timeWithTimezoneBehavior = SimpleValueBehavior.PASS_THROUGH,
        ),
    )

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
    override fun testBasicWrite() {
        super.testBasicWrite()
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
