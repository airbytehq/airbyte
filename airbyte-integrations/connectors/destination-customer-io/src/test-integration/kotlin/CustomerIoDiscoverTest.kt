/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.discover.DiscoverIntegrationTest
import io.airbyte.cdk.load.discover.DiscoverTestConfig
import io.airbyte.integrations.destination.customerio.CustomerIoSpecification
import java.nio.file.Files
import java.nio.file.Path

class CustomerIoDiscoverTest :
    DiscoverIntegrationTest<CustomerIoSpecification>(
        successConfigFilenames =
            listOf(
                DiscoverTestConfig(
                    configContents = Files.readString(Path.of("secrets/config.json")),
                )
            ),
    )
