/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.json.Jsons.emptyObject
import java.util.*

class SnowflakeInternalStagingCaseInsensitiveTypingDedupingTest :
    AbstractSnowflakeTypingDedupingTest(forceUppercaseIdentifiers = true) {
    override val configPath: String
        get() = "secrets/1s1t_case_insensitive.json"

    @Throws(Exception::class)
    override fun dumpRawTableRecords(streamNamespace: String?, streamName: String): List<JsonNode> {
        val records: List<JsonNode> = super.dumpRawTableRecords(streamNamespace, streamName)
        return records
            .stream()
            .map { record: JsonNode ->
                // Downcase the column names.
                // RecordDiffer expects the raw table column names to be lowercase.
                // TODO we should probably provide a way to mutate the expected data?
                val mutatedRecord = emptyObject() as ObjectNode
                record.fields().forEachRemaining { entry: Map.Entry<String, JsonNode> ->
                    mutatedRecord.set<JsonNode>(
                        entry.key.lowercase(Locale.getDefault()),
                        entry.value
                    )
                }
                mutatedRecord
            }
            .toList()
    }
}
