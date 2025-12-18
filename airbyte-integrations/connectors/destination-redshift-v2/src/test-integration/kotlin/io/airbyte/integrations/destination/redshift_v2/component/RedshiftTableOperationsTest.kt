/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.component

import io.airbyte.cdk.load.component.TableOperationsFixtures
import io.airbyte.cdk.load.component.TableOperationsSuite
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.integrations.destination.redshift_v2.client.RedshiftAirbyteClient
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

@MicronautTest(environments = ["component"])
@Execution(ExecutionMode.CONCURRENT)
class RedshiftTableOperationsTest(
    override val client: RedshiftAirbyteClient,
    override val testClient: RedshiftTestTableOperationsClient,
    override val schemaFactory: TableSchemaFactory,
) : TableOperationsSuite {
    // Redshift uses lowercase column names
    override val airbyteMetaColumnMapping = Meta.COLUMN_NAMES.associateWith { it }

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
            columnNameMapping = RedshiftComponentTestFixtures.testMapping,
        )
    }

    @Test
    override fun `count table rows`() {
        super.`count table rows`(columnNameMapping = RedshiftComponentTestFixtures.testMapping)
    }

    @Test
    override fun `overwrite tables`() {
        super.`overwrite tables`(
            sourceInputRecords = TableOperationsFixtures.OVERWRITE_SOURCE_RECORDS,
            targetInputRecords = TableOperationsFixtures.OVERWRITE_TARGET_RECORDS,
            expectedRecords = TableOperationsFixtures.OVERWRITE_EXPECTED_RECORDS,
            columnNameMapping = RedshiftComponentTestFixtures.testMapping,
        )
    }

    @Test
    override fun `copy tables`() {
        super.`copy tables`(
            sourceInputRecords = TableOperationsFixtures.OVERWRITE_SOURCE_RECORDS,
            targetInputRecords = TableOperationsFixtures.OVERWRITE_TARGET_RECORDS,
            expectedRecords = TableOperationsFixtures.COPY_EXPECTED_RECORDS,
            columnNameMapping = RedshiftComponentTestFixtures.testMapping,
        )
    }

    @Test
    override fun `get generation id`() {
        super.`get generation id`(columnNameMapping = RedshiftComponentTestFixtures.testMapping)
    }

    // TODO: Upsert test uses TEST_INTEGER_SCHEMA for target table which only has 'test' column,
    // but the Dedupe import type has 'id' as primary key. The test needs schema alignment.
    // The testDedup integration test validates full upsert functionality end-to-end.
    @Test
    @Disabled("Test framework creates target table with schema missing the primary key column")
    override fun `upsert tables`() {
        super.`upsert tables`(
            sourceInputRecords = TableOperationsFixtures.UPSERT_SOURCE_RECORDS,
            targetInputRecords = TableOperationsFixtures.UPSERT_TARGET_RECORDS,
            expectedRecords = TableOperationsFixtures.UPSERT_EXPECTED_RECORDS,
            columnNameMapping = RedshiftComponentTestFixtures.idTestWithCdcMapping,
        )
    }
}
