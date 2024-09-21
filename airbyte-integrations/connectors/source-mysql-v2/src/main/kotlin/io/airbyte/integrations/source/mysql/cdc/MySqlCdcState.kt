/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.AirbyteSchemaHistoryStorage
import java.util.*

class MySqlCdcState(opaqueStateValue: OpaqueStateValue) {
    val savedOffset: JsonNode
    private val savedSchemaHistory: JsonNode?
    private val isSavedSchemaHistoryCompressed: Boolean

    init {
        val savedStatePresent = opaqueStateValue.get(STATE) != null
        this.savedOffset = opaqueStateValue.get(STATE).get(MYSQL_CDC_OFFSET)
        if (savedOffset == null) {
            throw error("Saved offset should not be null")
        }
        this.savedSchemaHistory = opaqueStateValue.get(STATE).get(MYSQL_DB_HISTORY)
        this.isSavedSchemaHistoryCompressed =
            savedStatePresent &&
                opaqueStateValue.get(STATE).has(IS_COMPRESSED) &&
                opaqueStateValue.get(STATE).get(IS_COMPRESSED).asBoolean()
    }

    fun getSavedSchemaHistory(): AirbyteSchemaHistoryStorage.SchemaHistory<Optional<JsonNode>> {
        return AirbyteSchemaHistoryStorage.SchemaHistory(
            Optional.ofNullable<JsonNode>(savedSchemaHistory),
            isSavedSchemaHistoryCompressed,
        )
    }

    companion object {
        const val STATE: String = "state"
        const val MYSQL_CDC_OFFSET: String = "mysql_cdc_offset"
        const val MYSQL_DB_HISTORY: String = "mysql_db_history"
        const val IS_COMPRESSED: String = "is_compressed"
        const val COMPRESSION_ENABLED: Boolean = true
    }
}
