/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.writer

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.load.model.http.HttpRequester


data class BatchRequestWriter(@JsonProperty("objects") val objects: List<WritableObject>, @JsonProperty("requester") val requester: HttpRequester) : Writer
