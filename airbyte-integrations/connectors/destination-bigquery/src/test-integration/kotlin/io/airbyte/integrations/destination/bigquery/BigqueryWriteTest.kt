/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.toolkits.load.db.orchestration.ColumnNameModifyingMapper
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.write.AllTypesBehavior
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigqueryColumnNameGenerator
import java.nio.file.Path
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
        BigqueryDestinationCleaner(configContents.deserializeToNode()),
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

abstract class BigqueryTDWriteTest(
    configContents: String,
) :
    BigqueryWriteTest(
        configContents = configContents,
        BigqueryFinalTableDataDumper,
        ColumnNameModifyingMapper(BigqueryColumnNameGenerator()),
        isStreamSchemaRetroactive = true,
        preserveUndeclaredFields = false,
        supportsDedup = true,
        nullEqualsUnset = true,
        StronglyTyped(
            convertAllValuesToString = false,
            topLevelFloatLosesPrecision = true,
            nestedFloatLosesPrecision = false,
            integerCanBeLarge = false,
        ),
    )

// TODO we should make the config stuff less dumb, this is just the minimal wiring to get something
// that works
class StandardInsertRawOverrideDisableTd :
    BigqueryRawTablesWriteTest(
        BigQueryDestinationTestUtils.createConfig(
                configFile =
                    Path.of("secrets/credentials-1s1t-disabletd-standard-raw-override.json"),
                datasetId = DEFAULT_NAMESPACE_PLACEHOLDER,
                stagingPath = "test_path/$DEFAULT_NAMESPACE_PLACEHOLDER",
                rawDatasetId = "${DEFAULT_NAMESPACE_PLACEHOLDER}_raw_dataset",
            )
            .serializeToString(),
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
    BigqueryTDWriteTest(
        BigQueryDestinationTestUtils.createConfig(
                configFile = Path.of("secrets/credentials-1s1t-standard-raw-override.json"),
                datasetId = DEFAULT_NAMESPACE_PLACEHOLDER,
                stagingPath = "test_path/$DEFAULT_NAMESPACE_PLACEHOLDER",
                rawDatasetId = "${DEFAULT_NAMESPACE_PLACEHOLDER}_raw_dataset",
            )
            .serializeToString(),
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
    BigqueryTDWriteTest(
        BigQueryDestinationTestUtils.createConfig(
                configFile = Path.of("secrets/credentials-1s1t-standard.json"),
                datasetId = DEFAULT_NAMESPACE_PLACEHOLDER,
                stagingPath = "test_path/$DEFAULT_NAMESPACE_PLACEHOLDER",
            )
            .serializeToString(),
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

class GcsRawOverrideDisableTd :
    BigqueryRawTablesWriteTest(
        BigQueryDestinationTestUtils.createConfig(
                configFile = Path.of("secrets/credentials-1s1t-disabletd-gcs-raw-override.json"),
                datasetId = DEFAULT_NAMESPACE_PLACEHOLDER,
                stagingPath = "test_path/$DEFAULT_NAMESPACE_PLACEHOLDER",
                rawDatasetId = "${DEFAULT_NAMESPACE_PLACEHOLDER}_raw_dataset",
            )
            .serializeToString(),
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

class GcsRawOverride :
    BigqueryTDWriteTest(
        BigQueryDestinationTestUtils.createConfig(
                configFile = Path.of("secrets/credentials-1s1t-gcs-raw-override.json"),
                datasetId = DEFAULT_NAMESPACE_PLACEHOLDER,
                stagingPath = "test_path/$DEFAULT_NAMESPACE_PLACEHOLDER",
                rawDatasetId = "${DEFAULT_NAMESPACE_PLACEHOLDER}_raw_dataset",
            )
            .serializeToString(),
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

class Gcs :
    BigqueryTDWriteTest(
        BigQueryDestinationTestUtils.createConfig(
                configFile = Path.of("secrets/credentials-1s1t-gcs.json"),
                datasetId = DEFAULT_NAMESPACE_PLACEHOLDER,
                stagingPath = "test_path/$DEFAULT_NAMESPACE_PLACEHOLDER",
            )
            .serializeToString(),
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}
