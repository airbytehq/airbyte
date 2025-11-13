/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.component

import io.airbyte.cdk.load.component.TableOperationsSuite
import io.airbyte.integrations.destination.mysql_v2.client.MysqlAirbyteClient
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

@MicronautTest(environments = ["component"])
@Execution(ExecutionMode.CONCURRENT)
class MysqlTableOperationsTest : TableOperationsSuite {
    @Inject override lateinit var client: MysqlAirbyteClient
    @Inject override lateinit var testClient: MysqlTestTableOperationsClient

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
    override fun `get generation id`() {
        super.`get generation id`()
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
    override fun `upsert tables`() {
        super.`upsert tables`()
    }
}
