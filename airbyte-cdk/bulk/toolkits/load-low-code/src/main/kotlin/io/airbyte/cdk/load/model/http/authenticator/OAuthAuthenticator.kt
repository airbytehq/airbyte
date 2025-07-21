/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.http.authenticator

import com.fasterxml.jackson.annotation.JsonProperty

data class OAuthAuthenticator(
    @JsonProperty("url") val url: String,
    @JsonProperty("client_id") val clientId: String,
    @JsonProperty("client_secret") val clientSecret: String,
    @JsonProperty("refresh_token") val refreshToken: String,
) : Authenticator
