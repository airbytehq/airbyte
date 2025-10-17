/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.component

import io.airbyte.cdk.load.component.TableOperationsSuite
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseAirbyteClient
import jakarta.inject.Inject
import org.junit.jupiter.api.Test

class ClickhouseTableOperationsTest : TableOperationsSuite {
    @Inject override lateinit var client: ClickhouseAirbyteClient

    @Test
    override fun `connect to database`() {
        super.`connect to database`()
    }

    @Test
    override fun `create and drop namespaces`() {
        super.`create and drop namespaces`()
    }

    @Test
    override fun `create and drop tables`() {
        super.`create and drop tables`()
    }

    @Test
    override fun `insert records`() {
        super.`insert records`()
    }

    @Test
    override fun `count table rows`() {
        super.`count table rows`()
    }

    @Test
    override fun `overwrite tables`() {
        super.`overwrite tables`()
    }

    @Test
    override fun `copy tables`() {
        super.`copy tables`()
    }

    @Test
    override fun `get generation id`() {
        super.`get generation id`()
    }
}
