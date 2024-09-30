package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode

data class MysqlJdbcStreamStateValue(
    @JsonProperty("cursor") val cursors: String,
    @JsonProperty("version") val version: Int,
    @JsonProperty("state_type") val stateType: String,
    @JsonProperty("stream_name") val streamName: String,
    @JsonProperty("cursor_field") val cursorField: List<String>,
    @JsonProperty("stream_namespace") val streamNamespace: String,
    @JsonProperty("cursor_record_count") val cursorRecordCount: Int,
    )
