/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.component

import io.airbyte.cdk.load.component.TableOperationsFixtures
import io.airbyte.cdk.load.component.TableOperationsSuite
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.airbyte.integrations.destination.postgres.component.PostgresComponentTestFixtures.idTestWithCdcMapping
import io.airbyte.integrations.destination.postgres.component.PostgresComponentTestFixtures.testMapping
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["component"])
class PostgresTableOperationsTest(
    override val client: PostgresAirbyteClient,
    override val testClient: PostgresTestTableOperationsClient,
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
        super.`insert records`(
            inputRecords = TableOperationsFixtures.SINGLE_TEST_RECORD_INPUT,
            expectedRecords = TableOperationsFixtures.SINGLE_TEST_RECORD_EXPECTED,
            columnNameMapping = testMapping,
        )
    }

    @Test
    override fun `count table rows`() {
        super.`count table rows`(columnNameMapping = testMapping)
    }

    @Test
    override fun `overwrite tables`() {
        super.`overwrite tables`(
            sourceInputRecords = TableOperationsFixtures.OVERWRITE_SOURCE_RECORDS,
            targetInputRecords = TableOperationsFixtures.OVERWRITE_TARGET_RECORDS,
            expectedRecords = TableOperationsFixtures.OVERWRITE_EXPECTED_RECORDS,
            columnNameMapping = testMapping,
        )
    }

    @Test
    override fun `copy tables`() {
        super.`copy tables`(
            sourceInputRecords = TableOperationsFixtures.OVERWRITE_SOURCE_RECORDS,
            targetInputRecords = TableOperationsFixtures.OVERWRITE_TARGET_RECORDS,
            expectedRecords = TableOperationsFixtures.COPY_EXPECTED_RECORDS,
            columnNameMapping = testMapping,
        )
    }

    @Test
    override fun `get generation id`() {
        super.`get generation id`(columnNameMapping = testMapping)
    }

    @Test
    override fun `upsert tables`() {
        super.`upsert tables`(
            sourceInputRecords = TableOperationsFixtures.UPSERT_SOURCE_RECORDS,
            targetInputRecords = TableOperationsFixtures.UPSERT_TARGET_RECORDS,
            expectedRecords = TableOperationsFixtures.UPSERT_EXPECTED_RECORDS,
            columnNameMapping = idTestWithCdcMapping,
        )
    }
}
