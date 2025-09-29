/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.http

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.load.model.http.authenticator.Authenticator
import io.airbyte.cdk.load.model.http.body.Body

/** Describes a HTTP request configuration. */
data class HttpRequester(
    @JsonProperty("type") val type: String = "HttpRequester",
    @JsonProperty("url") val url: String,
    @JsonProperty("method") val method: HttpMethod,
    @JsonProperty("headers") val headers: Map<String, String>? = emptyMap(),
    @JsonProperty("authenticator") val authenticator: Authenticator? = null,
    // FIXME The possible implementation of Body feels weird as we have bodies which require logic
    // to be build and some do not. For example, if I were to need to pass a body during the
    // discover, this body could not be a `JsonBatchBody` because the accumulation of records is not
    // possible in this flow
    @JsonProperty("body") val body: Body? = null,
)
