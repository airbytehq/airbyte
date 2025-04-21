/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.FakeDataDumper
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
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
    preserveUndeclaredFields: Boolean,
) :
    BasicFunctionalityIntegrationTest(
        configContents = configContents,
        BigquerySpecification::class.java,
        dataDumper = dataDumper,
        NoopDestinationCleaner,
        isStreamSchemaRetroactive = true,
        supportsDedup = true,
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
        preserveUndeclaredFields = true,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
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
        FakeDataDumper,
        preserveUndeclaredFields = false,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
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
        preserveUndeclaredFields = true,
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
        FakeDataDumper,
        preserveUndeclaredFields = false,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}
