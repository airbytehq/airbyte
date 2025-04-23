/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
import java.nio.file.Path
import org.junit.jupiter.api.Test

abstract class BigqueryWriteTest(
    configContents: String,
    dataDumper: DestinationDataDumper,
    expectedRecordMapper: ExpectedRecordMapper,
    preserveUndeclaredFields: Boolean,
    supportsDedup: Boolean,
) :
    BasicFunctionalityIntegrationTest(
        configContents = configContents,
        BigquerySpecification::class.java,
        dataDumper,
        NoopDestinationCleaner,
        recordMangler = expectedRecordMapper,
        isStreamSchemaRetroactive = true,
        supportsDedup = supportsDedup,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        preserveUndeclaredFields = preserveUndeclaredFields,
        supportFileTransfer = false,
        commitDataIncrementally = true,
        allTypesBehavior =
            StronglyTyped(
                convertAllValuesToString = false,
                topLevelFloatLosesPrecision = true,
                nestedFloatLosesPrecision = false,
                integerCanBeLarge = false,
            ),
        configUpdater = BigqueryConfigUpdater,
        additionalMicronautEnvs = additionalMicronautEnvs,
    )

// TODO we should make the config stuff less dumb, this is just the minimal wiring to get something
// that works
class StandardInsertRawOverrideDisableTd :
    BigqueryWriteTest(
        BigQueryDestinationTestUtils.createConfig(
                configFile =
                    Path.of("secrets/credentials-1s1t-disabletd-standard-raw-override.json"),
                datasetId = DEFAULT_NAMESPACE_PLACEHOLDER,
                stagingPath = "test_path/$DEFAULT_NAMESPACE_PLACEHOLDER",
            )
            .serializeToString(),
        BigqueryRawTableDataDumper,
        UncoercedExpectedRecordMapper,
        preserveUndeclaredFields = true,
        supportsDedup = false,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
    @Test
    override fun testTruncateRefresh() {
        super.testTruncateRefresh()
    }
}

class StandardInsertRawOverride :
    BigqueryWriteTest(
        BigQueryDestinationTestUtils.createConfig(
                configFile = Path.of("secrets/credentials-1s1t-standard-raw-override.json"),
                datasetId = DEFAULT_NAMESPACE_PLACEHOLDER,
                stagingPath = "test_path/$DEFAULT_NAMESPACE_PLACEHOLDER",
            )
            .serializeToString(),
        BigqueryFinalTableDataDumper,
        NoopExpectedRecordMapper,
        preserveUndeclaredFields = false,
        supportsDedup = true,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
    @Test
    override fun testTruncateRefresh() {
        super.testTruncateRefresh()
    }
}

class GcsRawOverrideDisableTd :
    BigqueryWriteTest(
        BigQueryDestinationTestUtils.createConfig(
                configFile = Path.of("secrets/credentials-1s1t-disabletd-gcs-raw-override.json"),
                datasetId = DEFAULT_NAMESPACE_PLACEHOLDER,
                stagingPath = "test_path/$DEFAULT_NAMESPACE_PLACEHOLDER",
            )
            .serializeToString(),
        BigqueryRawTableDataDumper,
        UncoercedExpectedRecordMapper,
        preserveUndeclaredFields = true,
        supportsDedup = false,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

class GcsRawOverride :
    BigqueryWriteTest(
        BigQueryDestinationTestUtils.createConfig(
                configFile = Path.of("secrets/credentials-1s1t-gcs-raw-override.json"),
                datasetId = DEFAULT_NAMESPACE_PLACEHOLDER,
                stagingPath = "test_path/$DEFAULT_NAMESPACE_PLACEHOLDER",
            )
            .serializeToString(),
        BigqueryFinalTableDataDumper,
        NoopExpectedRecordMapper,
        preserveUndeclaredFields = false,
        supportsDedup = true,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}
