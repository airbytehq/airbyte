/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.component

import io.airbyte.cdk.load.component.ConnectorWiringSuite
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.write.DestinationWriter
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["component", "MockDestinationCatalog"])
class MongodbWiringTest(
    override val writer: DestinationWriter,
    override val client: TableOperationsClient,
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

    @Test
    override fun `can create append stream loader`() {
        super.`can create append stream loader`()
    }

    @Test
    override fun `can write one record`() {
        super.`can write one record`()
    }
}
