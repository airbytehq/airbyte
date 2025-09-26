/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.writer

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.load.model.http.HttpRequester
import io.airbyte.cdk.load.model.writer.rejected.RejectedRecords


data class BatchRequestWriter(
    @JsonProperty("objects") val objects: List<WritableObject>,
    @JsonProperty("requester") val requester: HttpRequester,
    @JsonProperty("rejected_records") val rejectedRecords: RejectedRecords,
) : Writer
