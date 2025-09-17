/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.retriever

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.load.model.http.HttpRequester

/**
 * Configuration for retriever component which makes an API request and extracts a target value from
 * the response
 */
data class Retriever(
    @JsonProperty("type") val type: String = "Retriever",
    @JsonProperty("http_requester") val httpRequester: HttpRequester,
    @JsonProperty("selector") val selector: List<String>,
)
