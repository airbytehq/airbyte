/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.postgres.PostgresContainerHelper
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.time.ZoneOffset

/**
 * PostgreSQL normalizes timestamptz values to UTC and doesn't preserve the original timezone
 * offset. It also strips null bytes from strings. This mapper converts expected
 * timestamp_with_timezone values to UTC and removes null characters for comparison.
 */
object PostgresTimestampNormalizationMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val sanitized = removeNullCharacters(expectedRecord.data)
        val normalized = normalizeTimestampsToUtc(sanitized)
        return expectedRecord.copy(data = normalized as ObjectValue)
    }

    private fun removeNullCharacters(value: AirbyteValue): AirbyteValue =
        when (value) {
            is StringValue -> StringValue(value.value.replace("\u0000", ""))
            is ArrayValue -> ArrayValue(value.values.map { removeNullCharacters(it) })
            is ObjectValue ->
                ObjectValue(
                    value.values.mapValuesTo(linkedMapOf()) { (_, v) -> removeNullCharacters(v) }
                )
            else -> value
        }

    private fun normalizeTimestampsToUtc(value: AirbyteValue): AirbyteValue =
        when (value) {
            is TimestampWithTimezoneValue ->
                TimestampWithTimezoneValue(value.value.withOffsetSameInstant(ZoneOffset.UTC))
            is ArrayValue -> ArrayValue(value.values.map { normalizeTimestampsToUtc(it) })
            is ObjectValue ->
                ObjectValue(
                    value.values.mapValuesTo(linkedMapOf()) { (_, v) ->
                        normalizeTimestampsToUtc(v)
                    }
                )
            else -> value
        }
}

object PostgresDataCleaner : DestinationCleaner {
    override fun cleanup() {
        // TODO: Implement cleanup logic to drop test schemas/tables
        // Similar to ClickhouseDataCleaner or MSSQLDataCleaner
    }
}

/** Builds a map of overrides for the test container environment. */
fun buildConfigOverridesForTestContainer(): MutableMap<String, String> {
    return mutableMapOf(
        "host" to PostgresContainerHelper.getHost(),
        "port" to PostgresContainerHelper.getPort().toString(),
        "database" to PostgresContainerHelper.getDatabaseName(),
        "username" to PostgresContainerHelper.getUsername(),
        "password" to PostgresContainerHelper.getPassword()
    )
}

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
                        changeNode["change"].textValue()
                    ),
                reason =
                    AirbyteRecordMessageMetaChange.Reason.fromValue(
                        changeNode["reason"].textValue()
                    )
            )
        }

    return OutputRecord.Meta(changes = changes, syncId = metaJson["sync_id"].longValue())
}
