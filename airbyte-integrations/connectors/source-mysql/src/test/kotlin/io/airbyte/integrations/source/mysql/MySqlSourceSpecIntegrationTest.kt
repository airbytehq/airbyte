/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.SyncsTestFixture
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class MySqlSourceSpecIntegrationTest {
    @Test
    fun testSpec() {
        SyncsTestFixture.testSpec("expected-spec.json")
    }

    @Test
    fun testCdcDocumentationLinkReferencesMysqlDocs() {
        val connectionSpecification =
            CliRunner.source("spec").run().specs().last().connectionSpecification
        val cdcDescription =
            connectionSpecification["properties"]["replication_method"]["oneOf"][1]["description"]
                .asText()

        assertEquals(
            "<i>Recommended</i> - Incrementally reads new inserts, updates, and deletes using MySQL's " +
                "<a href=\"https://docs.airbyte.com/integrations/sources/mysql/#change-data-capture-cdc\">" +
                " change data capture feature</a>. This must be enabled on your database.",
            cdcDescription,
        )
        assertTrue(cdcDescription.contains("/integrations/sources/mysql/"))
        assertFalse(cdcDescription.contains("/integrations/sources/mssql/"))
    }
}
