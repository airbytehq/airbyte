/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.component

import io.airbyte.cdk.load.component.CoreTableOperationsSuite
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseAirbyteClient
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Test

@MicronautTest
class ClickhouseTableOperationsTest : CoreTableOperationsSuite {
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

    override fun `count table rows`() {
        super.`count table rows`()
    }

    override fun `overwrite tables`() {
        super.`overwrite tables`()
    }

    override fun `copy tables`() {
        super.`copy tables`()
    }

    override fun `upsert tables`() {
        super.`upsert tables`()
    }

    override fun `get generation id`() {
        super.`get generation id`()
    }
}
