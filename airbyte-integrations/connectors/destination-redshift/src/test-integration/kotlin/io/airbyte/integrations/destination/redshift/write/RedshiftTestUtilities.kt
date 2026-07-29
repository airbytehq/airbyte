/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Files
import java.nio.file.Path
import java.time.ZoneOffset

private val logger = KotlinLogging.logger {}

/** Path to the Redshift config secrets file used by integration tests. */
const val CONFIG_PATH = "secrets/test_cluster.json"

/**
 * Maps expected records to match Redshift's actual storage behavior:
 * - Normalizes timestamptz and timetz values to UTC, since Redshift stores all timezone-aware
 * temporal types internally as UTC and the JDBC driver returns them in UTC.
 */
object RedshiftExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val normalized = normalizeToUtc(expectedRecord.data)
        return expectedRecord.copy(data = normalized as ObjectValue)
    }

    private fun normalizeToUtc(value: AirbyteValue): AirbyteValue =
        when (value) {
            is TimestampWithTimezoneValue ->
                TimestampWithTimezoneValue(value.value.withOffsetSameInstant(ZoneOffset.UTC))
            is TimeWithTimezoneValue ->
                TimeWithTimezoneValue(value.value.withOffsetSameInstant(ZoneOffset.UTC))
            is ArrayValue -> ArrayValue(value.values.map { normalizeToUtc(it) })
            is ObjectValue ->
                ObjectValue(value.values.mapValuesTo(linkedMapOf()) { (_, v) -> normalizeToUtc(v) })
            else -> value
        }
}

/**
 * Cleans up old test schemas from Redshift. Connects to the cluster, lists schemas matching the
 * test namespace pattern, and drops schemas older than the retention period.
 */
object RedshiftDataCleaner : DestinationCleaner {
    override fun cleanup() {
        val configPath = Path.of(CONFIG_PATH)
        if (!Files.exists(configPath)) {
            logger.warn { "Secrets file not found at $CONFIG_PATH, skipping cleanup" }
            return
        }

        val dataSource = RedshiftTestDataSourceProvider.get()
        dataSource.connection.use { connection ->
            val statement = connection.createStatement()
            val schemasToDrop = mutableListOf<String>()
            val schemas =
                statement.executeQuery(
                    """
                    SELECT schema_name
                    FROM information_schema.schemata
                    WHERE schema_name LIKE '%test%'
                    """.trimIndent(),
                )
            while (schemas.next()) {
                val schemaName = schemas.getString("schema_name")
                if (IntegrationTest.isNamespaceOld(schemaName)) {
                    schemasToDrop.add(schemaName)
                }
            }
            if (schemasToDrop.isNotEmpty()) {
                logger.info { "Dropping ${schemasToDrop.size} old test schemas: $schemasToDrop" }
                val dropSql =
                    schemasToDrop.joinToString("\n") { schemaName ->
                        "DROP SCHEMA IF EXISTS \"$schemaName\" CASCADE;"
                    }
                statement.execute(dropSql)
            }
        }
    }
}

/** Parses the `_airbyte_meta` SUPER column JSON into an [OutputRecord.Meta] object. */
fun stringToMeta(metaAsString: String?): OutputRecord.Meta? {
    if (metaAsString.isNullOrEmpty()) {
        return null
    }
    val metaJson = Jsons.readTree(metaAsString)

    val changes =
        (metaJson["changes"] as ArrayNode).map { change ->
            val changeNode = change as JsonNode
            Meta.Change(
                field = changeNode["field"].textValue(),
                change =
                    AirbyteRecordMessageMetaChange.Change.fromValue(
                        changeNode["change"].textValue(),
                    ),
                reason =
                    AirbyteRecordMessageMetaChange.Reason.fromValue(
                        changeNode["reason"].textValue(),
                    ),
            )
        }

    return OutputRecord.Meta(changes = changes, syncId = metaJson["sync_id"].longValue())
}
