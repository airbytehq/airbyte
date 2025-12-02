/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.check

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.gcs_data_lake.GcsDataLakeTestUtil.BIGLAKE_CONFIG_PATH
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeSpecification
import java.nio.file.Files
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

class GcsDataLakeCheckTest :
    CheckIntegrationTest<GcsDataLakeSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(Files.readString(BIGLAKE_CONFIG_PATH)),
            ),
        // TODO: Add configs that are expected to fail `check` for validation testing
        failConfigFilenamesAndFailureReasons = mapOf(),
    ) {
    @Test
    @Timeout(5, unit = TimeUnit.MINUTES)
    override fun testSuccessConfigs() {
        super.testSuccessConfigs()
    }
}
