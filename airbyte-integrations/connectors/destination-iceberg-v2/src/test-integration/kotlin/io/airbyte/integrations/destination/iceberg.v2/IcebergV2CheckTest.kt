/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.iceberg.v2.IcebergV2TestUtil.PATH

class IcebergV2CheckTest :
    CheckIntegrationTest<IcebergV2Specification>(
        successConfigFilenames = listOf(CheckTestConfig(PATH)),
        // TODO we maybe should add some configs that are expected to fail `check`
        failConfigFilenamesAndFailureReasons = mapOf(),
    )
