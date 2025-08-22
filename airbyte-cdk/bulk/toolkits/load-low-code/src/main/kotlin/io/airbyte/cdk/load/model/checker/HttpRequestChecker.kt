/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.checker

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.load.model.http.HttpRequester

/**
 * Configuration for destination check operations. Performs a HTTP request to the destination API to
 * check if the configuration is valid.
 */
data class HttpRequestChecker(@JsonProperty("requester") val requester: HttpRequester) : Checker
