/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.s3_data_lake.S3DataLakeTestUtil.GLUE_CONFIG_PATH

class S3DataLakeCheckTest :
    CheckIntegrationTest<S3DataLakeSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(GLUE_CONFIG_PATH),
            ),
        // TODO we maybe should add some configs that are expected to fail `check`
        failConfigFilenamesAndFailureReasons = mapOf(),
        additionalMicronautEnvs = S3DataLakeDestination.additionalMicronautEnvs,
    )
