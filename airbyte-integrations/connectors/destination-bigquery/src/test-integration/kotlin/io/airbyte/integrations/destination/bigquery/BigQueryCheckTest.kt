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
                    BigQueryDestinationTestUtils.createConfig(
                        "secrets/credentials-badproject.json"
                    ),
                    name = "bad project",
                ) to
                    Pattern.compile(
                        "Access Denied: Project fake: User does not have bigquery.datasets.create permission in project fake"
                    ),
                // these tests somehow hang in CI.
                // CheckTestConfig(
                //     BigQueryDestinationTestUtils.createConfig(
                //         "secrets/credentials-no-edit-public-schema-role.json"
                //     ),
                //     name = "no edit public schema role",
                // ) to Pattern.compile("Permission bigquery.tables.create denied"),
                // CheckTestConfig(
                //     BigQueryDestinationTestUtils.createConfig(
                //         "secrets/credentials-standard-no-dataset-creation.json"
                //     ),
                //     name = "no dataset creation",
                // ) to Pattern.compile("Permission bigquery.tables.create denied"),
                // somehow this test causes the docker container to emit a malformed log message
                // (it's truncated).
                // CheckTestConfig(
                //     BigQueryDestinationTestUtils.createConfig(
                //         "secrets/credentials-1s1t-gcs-bad-copy-permission.json"
                //     ),
                //     name = "gcs bad copy permission",
                // ) to Pattern.compile("Permission bigquery.tables.updateData denied on table"),
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
