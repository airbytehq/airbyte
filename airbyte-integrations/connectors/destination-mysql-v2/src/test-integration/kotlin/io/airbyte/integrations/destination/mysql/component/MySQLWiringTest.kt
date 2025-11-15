package io.airbyte.integrations.destination.mysql.component

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.component.ConnectorWiringSuite
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.write.DestinationWriter
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["component", "MockDestinationCatalog"])
class MySQLWiringTest(
    override val writer: DestinationWriter,
    override val client: TableOperationsClient,
    override val aggregateFactory: AggregateFactory,
) : ConnectorWiringSuite {

    // Override to use stream from MockDestinationCatalog
    override fun createTestStream(
        namespace: String,
        name: String,
        importType: ImportType
    ): DestinationStream {
        // Return stream1 from mock catalog
        return MockDestinationCatalogFactory.stream1
    }

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
