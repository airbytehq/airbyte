import io.airbyte.cdk.load.discover.DiscoverIntegrationTest
import io.airbyte.cdk.load.discover.DiscoverTestConfig
import io.airbyte.integrations.destination.shelby.ShelbySpecification
import io.airbyte.protocol.models.v0.DestinationCatalog

class ShelbyDiscoverTest :
    DiscoverIntegrationTest<ShelbySpecification>(
        successConfigFilenames = listOf(
            DiscoverTestConfig(
                configContents = "{}",
                expectedCatalog = DestinationCatalog(),
            )
        )
    )
