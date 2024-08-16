package io.airbyte.integrations.base.destination

import com.fasterxml.jackson.databind.JsonNode
import org.junit.jupiter.api.Test

abstract class RefreshesIntegrationTest(
    destinationFactory: DestinationFactory,
    config: JsonNode,
) : IntegrationTest(
    destinationFactory,
    config,
) {

    @Test
    open fun truncateRefresh() {
        // run two syncs, dump records, etc
    }
}
