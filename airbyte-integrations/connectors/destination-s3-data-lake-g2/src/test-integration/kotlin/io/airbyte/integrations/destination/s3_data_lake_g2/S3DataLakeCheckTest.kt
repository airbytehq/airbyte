/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake_g2

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.s3_data_lake_g2.S3DataLakeTestUtil.GLUE_CONFIG_PATH
import io.airbyte.integrations.destination.s3_data_lake_g2.spec.S3DataLakeSpecification
import java.nio.file.Files

class S3DataLakeCheckTest :
    CheckIntegrationTest<S3DataLakeSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(Files.readString(GLUE_CONFIG_PATH)),
            ),
        // TODO we maybe should add some configs that are expected to fail `check`
        failConfigFilenamesAndFailureReasons = mapOf(),
        additionalMicronautEnvs = S3DataLakeDestination.additionalMicronautEnvs,
    )
