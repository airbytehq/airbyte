package io.airbyte.cdk.load.model.http.body.batch

import com.fasterxml.jackson.annotation.JsonProperty

data class JsonBatchEntry(
    @JsonProperty("content") val content: String,
    @JsonProperty("field") val field: List<String>
)
