package io.airbyte.integrations.destination.mysql.check

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.mysql.spec.MySQLSpecification
import java.nio.file.Files
import java.nio.file.Path

class MySQLCheckTest :
    CheckIntegrationTest<MySQLSpecification>(
        successConfigFilenames = listOf(
            CheckTestConfig(
                configContents = Files.readString(Path.of("secrets/test-instance.json"))
            ),
        ),
        failConfigFilenamesAndFailureReasons = emptyMap(),
    )
