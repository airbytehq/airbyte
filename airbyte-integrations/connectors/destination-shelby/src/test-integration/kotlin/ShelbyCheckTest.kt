import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.integrations.destination.shelby.ShelbySpecification

class ShelbyCheckTest :
    CheckIntegrationTest<ShelbySpecification>(
        successConfigFilenames = listOf(
            CheckTestConfig(configContents = "{}")
        ),
        failConfigFilenamesAndFailureReasons = emptyMap(),
    )
