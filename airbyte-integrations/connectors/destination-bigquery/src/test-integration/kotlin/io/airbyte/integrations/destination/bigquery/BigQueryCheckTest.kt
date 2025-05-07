/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.bigquery.spec.BigquerySpecification
import java.util.regex.Pattern
import org.junit.jupiter.api.Test

class BigQueryCheckTest :
    CheckIntegrationTest<BigquerySpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(BigQueryDestinationTestUtils.standardInsertConfig),
            ),
        failConfigFilenamesAndFailureReasons =
            mapOf(
                CheckTestConfig(
                    BigQueryDestinationTestUtils.createConfig("secrets/credentials-badproject.json")
                ) to
                    Pattern.compile(
                        "Access Denied: Project fake: User does not have bigquery.datasets.create permission in project fake"
                    ),
                CheckTestConfig(
                    BigQueryDestinationTestUtils.createConfig(
                        "secrets/credentials-no-edit-public-schema-role.json"
                    )
                ) to Pattern.compile("Permission bigquery.tables.create denied"),
                CheckTestConfig(
                    BigQueryDestinationTestUtils.createConfig(
                        "secrets/credentials-standard-no-dataset-creation.json"
                    )
                ) to Pattern.compile("Permission bigquery.tables.create denied"),
                CheckTestConfig(
                    BigQueryDestinationTestUtils.createConfig(
                        "secrets/credentials-standard-non-billable-project.json"
                    )
                ) to Pattern.compile("Billing has not been enabled for this project"),
                CheckTestConfig(
                    BigQueryDestinationTestUtils.createConfig(
                        "secrets/credentials-1s1t-gcs-bad-copy-permission.json"
                    )
                ) to Pattern.compile("Permission bigquery.tables.updateData denied on table"),
            ),
        additionalMicronautEnvs = additionalMicronautEnvs,
    ) {
    @Test
    override fun testSuccessConfigs() {
        super.testSuccessConfigs()
    }

    @Test
    override fun testFailConfigs() {
        super.testFailConfigs()
    }
}
