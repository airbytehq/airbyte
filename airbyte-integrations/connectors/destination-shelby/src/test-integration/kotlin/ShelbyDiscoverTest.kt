import io.airbyte.cdk.load.discover.DiscoverIntegrationTest
import io.airbyte.cdk.load.discover.DiscoverTestConfig
import io.airbyte.integrations.destination.shelby.ShelbySpecification

class ShelbyDiscoverTest :
    DiscoverIntegrationTest<ShelbySpecification>(
        successConfigFilenames = listOf(
            DiscoverTestConfig(
                configContents = "{}",
            )
        ),
        failConfigFilenamesAndFailureReasons = emptyMap(),
    )
