/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.customerio.CustomerIoSpecification
import java.nio.file.Files
import java.nio.file.Path
import java.util.regex.Pattern

class CustomerIoCheckTest :
    CheckIntegrationTest<CustomerIoSpecification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(
                    configContents = Files.readString(Path.of("secrets/config.json")),
                )
            ),
        failConfigFilenamesAndFailureReasons =
            mapOf(
                CheckTestConfig(
                    configContents = Files.readString(Path.of("secrets/invalid-config.json"))
                ) to Pattern.compile("Expected status code to be 200 but was.*"),
            ),
    )
