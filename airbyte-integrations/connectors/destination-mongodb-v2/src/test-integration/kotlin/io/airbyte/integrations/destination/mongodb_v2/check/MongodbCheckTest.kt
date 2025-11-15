/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.check

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.mongodb_v2.MongodbConfigUpdater
import io.airbyte.integrations.destination.mongodb_v2.config.MongodbSpecification
import java.nio.file.Path

class MongodbCheckTest :
    CheckIntegrationTest<MongodbSpecification>(
        successConfigFilenames = listOf(
            CheckTestConfig(configContents = Path.of("secrets/config.json").toFile().readText()),
        ),
        failConfigFilenamesAndFailureReasons = emptyMap(),
        configUpdater = MongodbConfigUpdater(),
    )
