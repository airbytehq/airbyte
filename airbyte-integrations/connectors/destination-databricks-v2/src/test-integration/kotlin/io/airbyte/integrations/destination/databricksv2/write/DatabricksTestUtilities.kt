/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.OutputRecord

const val CONFIG_PATH = "secrets/config.json"

/**
 * Identity mapper -- Databricks stores temporal types natively and preserves values as-is, so no
 * normalization is needed (unlike Redshift which converts timestamps to UTC).
 */
object DatabricksExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord =
        expectedRecord
}

/**
 * Cleans up old test namespaces from Databricks. Finds schemas matching `test%` and drops those
 * older than the integration test threshold.
 */
object DatabricksDataCleaner : DestinationCleaner {
    override fun cleanup() {
        val config = DatabricksTestConfigProvider.configFromFile()
        val dataSource = DatabricksTestDataSourceProvider.get(config)
        dataSource.connection.use { conn ->
            conn.createStatement().use { stmt ->
                val schemas = mutableListOf<String>()
                stmt
                    .executeQuery(
                        """
                        SELECT schema_name FROM ${config.database}.information_schema.schemata
                        WHERE catalog_name = '${config.database}'
                        AND schema_name LIKE 'test%'
                        """.trimIndent(),
                    )
                    .use { rs ->
                        while (rs.next()) {
                            schemas.add(rs.getString("schema_name"))
                        }
                    }

                schemas
                    .filter { IntegrationTest.isNamespaceOld(it) }
                    .forEach { schema ->
                        stmt.execute("DROP SCHEMA IF EXISTS `${config.database}`.`$schema` CASCADE")
                    }
            }
        }
    }
}
