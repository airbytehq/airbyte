package io.airbyte.cdk.load.model.http.body.batch

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.load.model.http.body.Body
import io.airbyte.cdk.load.model.http.body.size.BatchSize

data class JsonBatchBody(
    @JsonProperty("size") val size: BatchSize,
    @JsonProperty("entries") val entries: JsonBatchEntry
) : Body
