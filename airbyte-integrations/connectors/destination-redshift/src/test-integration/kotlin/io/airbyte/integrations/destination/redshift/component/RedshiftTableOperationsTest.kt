/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.component

import io.airbyte.cdk.load.component.TableOperationsSuite
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.integrations.destination.redshift.client.RedshiftAirbyteClient
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["component"])
class RedshiftTableOperationsTest(
    override val client: RedshiftAirbyteClient,
    override val testClient: RedshiftTestTableOperationsClient,
    override val schemaFactory: TableSchemaFactory,
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
    @Disabled(
        "CDK fixture (bulk-cdk-core-load 1.0.7) contains a 37-char UUID that exceeds Redshift's varchar(36) for _airbyte_raw_id. Re-enable once the CDK publishes a fix."
    )
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

    @Test
    override fun `upsert tables`() {
        super.`upsert tables`()
    }
}
