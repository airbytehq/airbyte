import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.integrations.destination.shelby.ShelbySpecification

class ShelbyCheckTest :
    CheckIntegrationTest<ShelbySpecification>(
        successConfigFilenames = emptyList(),
        failConfigFilenamesAndFailureReasons = emptyMap(),
    )
