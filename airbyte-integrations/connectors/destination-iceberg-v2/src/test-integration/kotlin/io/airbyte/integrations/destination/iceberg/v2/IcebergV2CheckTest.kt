/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.iceberg.v2.IcebergV2TestUtil.GLUE_CONFIG_PATH
import io.airbyte.integrations.destination.iceberg.v2.IcebergV2TestUtil.MINIMAL_CONFIG_PATH
import org.junit.jupiter.api.Disabled

@Disabled
class IcebergV2CheckTest :
    CheckIntegrationTest<IcebergV2Specification>(
        successConfigFilenames = listOf(
            CheckTestConfig(MINIMAL_CONFIG_PATH),
            CheckTestConfig(GLUE_CONFIG_PATH),
        ),
        // TODO we maybe should add some configs that are expected to fail `check`
        failConfigFilenamesAndFailureReasons = mapOf(),
    )
