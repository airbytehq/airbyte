/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.check

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Specification
import java.nio.file.Files
import java.nio.file.Path

class RedshiftCheckTest :
    CheckIntegrationTest<RedshiftV2Specification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(
                    Files.readString(Path.of("secrets/config_staging.json")),
                    name = "Valid Redshift connection (S3 staging)",
                ),
            ),
        failConfigFilenamesAndFailureReasons = emptyMap(),
    )
