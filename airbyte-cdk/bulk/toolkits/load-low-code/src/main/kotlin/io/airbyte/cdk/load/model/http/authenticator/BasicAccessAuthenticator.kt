/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.http.authenticator

import com.fasterxml.jackson.annotation.JsonProperty

/** Configuration for basic access authentication. */
data class BasicAccessAuthenticator(
    @JsonProperty("username") val username: String,
    @JsonProperty("password") val password: String
) : Authenticator
