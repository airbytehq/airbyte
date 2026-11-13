/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.component

import io.airbyte.cdk.load.component.ConnectorWiringSuite
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.integrations.destination.redshift_v2.client.RedshiftAirbyteClient
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

@MicronautTest(environments = ["component"])
@Execution(ExecutionMode.CONCURRENT)
class RedshiftWiringTest(
    override val writer: DestinationWriter,
    override val client: RedshiftAirbyteClient,
    override val aggregateFactory: AggregateFactory,
) : ConnectorWiringSuite {

    @Test
    override fun `all beans are injectable`() {
        super.`all beans are injectable`()
    }

    @Test
    override fun `writer setup completes`() {
        super.`writer setup completes`()
    }

    // These tests require a stream from the catalog, but the test creates a synthetic stream
    // that isn't in the initialStatuses map gathered during setup().
    // The BasicFunctionalityTest validates the full write path end-to-end.
    @Test
    @Disabled("Test creates synthetic stream not in catalog - use BasicFunctionalityTest instead")
    override fun `can create append stream loader`() {
        super.`can create append stream loader`()
    }

    @Test
    @Disabled("Test creates synthetic stream not in catalog - use BasicFunctionalityTest instead")
    override fun `can write one record`() {
        super.`can write one record`()
    }
}
