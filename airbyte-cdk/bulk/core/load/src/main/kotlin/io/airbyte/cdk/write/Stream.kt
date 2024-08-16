package io.airbyte.cdk.write

import com.fasterxml.jackson.annotation.JsonProperty

data class Stream(
    @JsonProperty("name") val name: String,
    @JsonProperty("namespace") val namespace: String? = null,
)
