/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.discover.DiscoverIntegrationTest
import io.airbyte.cdk.load.discover.DiscoverTestConfig
import io.airbyte.cdk.load.spec.NoopSpec
import java.nio.file.Files
import java.nio.file.Path

class CustomerIoDiscoverTest :
    DiscoverIntegrationTest<NoopSpec>(
        successConfigFilenames =
            listOf(
                DiscoverTestConfig(
                    configContents = Files.readString(Path.of("secrets/config.json")),
                )
            ),
    )
