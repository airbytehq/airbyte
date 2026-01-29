/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config.model

/**
 * Config object for JSON conversion options. May or may not overlap with configuration for .proto.
 */
data class JsonConverterConfig(
    val extractedAtAsTimestampWithTimezone: Boolean = true,
)
