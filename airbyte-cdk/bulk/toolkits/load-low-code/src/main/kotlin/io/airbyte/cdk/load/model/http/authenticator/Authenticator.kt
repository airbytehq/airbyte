/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.http.authenticator

import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo

/** Base interface for all authenticator types in declarative destinations. */
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "type")
@JsonSubTypes(
    JsonSubTypes.Type(value = BasicAccessAuthenticator::class, name = "BasicAccessAuthenticator"),
    JsonSubTypes.Type(value = OAuthAuthenticator::class, name = "OAuthAuthenticator"),
)
sealed interface Authenticator
