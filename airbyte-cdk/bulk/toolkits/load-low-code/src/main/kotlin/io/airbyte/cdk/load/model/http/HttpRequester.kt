/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.http

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.load.model.http.authenticator.Authenticator

/** Describes a HTTP request configuration. */
data class HttpRequester(
    @JsonProperty("type") val type: String = "HttpRequester",
    @JsonProperty("url") val url: String,
    @JsonProperty("method") val method: HttpMethod,
    @JsonProperty("authenticator") val authenticator: Authenticator? = null
)
