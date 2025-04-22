/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

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
    additionalMicronautEnvs: List<String> = emptyList()
) :
    BasicFunctionalityIntegrationTest(
        configContents = configContents,
        BigquerySpecification::class.java,
        FakeDataDumper,
        NoopDestinationCleaner,
        isStreamSchemaRetroactive = true,
        supportsDedup = true,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        preserveUndeclaredFields = false,
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
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

// @Disabled("Disabling until we have the full flow")
class GcsRawOverrideDisableTd :
    BigqueryWriteTest(
        BigQueryDestinationTestUtils.createConfig(
                configFile = Path.of("secrets/credentials-1s1t-disabletd-gcs-raw-override.json"),
                datasetId = DEFAULT_NAMESPACE_PLACEHOLDER,
                stagingPath = "test_path/$DEFAULT_NAMESPACE_PLACEHOLDER",
            )
            .serializeToString(),
        // TODO make a base BigqueryGcsWriteTest class to handle this
        additionalMicronautEnvs = additionalMicronautEnvs,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}
