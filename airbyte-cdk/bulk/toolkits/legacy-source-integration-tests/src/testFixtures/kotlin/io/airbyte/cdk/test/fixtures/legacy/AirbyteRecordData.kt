/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta

@JvmRecord
data class AirbyteRecordData(val rawRowData: JsonNode, val meta: AirbyteRecordMessageMeta)
