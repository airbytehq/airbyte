/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.component

import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableOperationsSuite
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["component"])
class MongodbTableOperationsTest(
    override val client: TableOperationsClient,
    override val testClient: TestTableOperationsClient,
) : TableOperationsSuite {

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
}
