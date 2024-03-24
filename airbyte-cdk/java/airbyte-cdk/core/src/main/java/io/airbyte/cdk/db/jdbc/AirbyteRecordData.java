/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.db.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;

public record AirbyteRecordData(JsonNode rawRowData, AirbyteRecordMessageMeta meta) {}
