/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.OutputRecord
import java.time.ZoneOffset

const val CONFIG_PATH = "secrets/oauth_config.json"

/**
 * Maps expected records to account for Databricks type storage:
 * - TIMESTAMP stores in UTC, losing the original offset. The JDBC driver also reports TIMESTAMP_NTZ
 * columns as "TIMESTAMP", so both types are read back as OffsetDateTime at UTC.
 * - Time types (with/without timezone) have no native Databricks equivalent and are stored as
 * STRING via [toString()][java.time.OffsetTime.toString], so expected time values are converted to
 * [StringValue] using the same method (which omits zero seconds, unlike ISO formatters).
 */
object DatabricksExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedData = mapValues(expectedRecord.data)
        return expectedRecord.copy(data = mappedData as ObjectValue)
    }

    private fun mapValues(value: AirbyteValue): AirbyteValue =
        when (value) {
            // Databricks TIMESTAMP stores in UTC -- normalize expected offset to UTC so
            // OffsetDateTime.compareTo() matches (it compares local time after instant).
            is TimestampWithTimezoneValue ->
                TimestampWithTimezoneValue(
                    value.value.toInstant().atOffset(ZoneOffset.UTC),
                )
            // JDBC driver reports TIMESTAMP_NTZ as "TIMESTAMP", so the data dumper returns
            // OffsetDateTime at UTC for both types. Convert expected NTZ to match.
            is TimestampWithoutTimezoneValue ->
                TimestampWithTimezoneValue(
                    value.value.toInstant(ZoneOffset.UTC).atOffset(ZoneOffset.UTC),
                )
            // Time types are stored as STRING via toString(), which omits zero seconds
            // (e.g. "11:34-01:00" not "11:34:00-01:00"). Use toString() to match.
            is TimeWithTimezoneValue -> StringValue(value.value.toString())
            is TimeWithoutTimezoneValue -> StringValue(value.value.toString())
            is ArrayValue -> ArrayValue(value.values.map { mapValues(it) })
            is ObjectValue ->
                ObjectValue(value.values.mapValuesTo(linkedMapOf()) { (_, v) -> mapValues(v) })
            else -> value
        }
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
