/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config.model

/** Config object for medium converter options. Used by both JSON and Protobuf converters. */
data class MediumConverterConfig(
    val extractedAtAsTimestampWithTimezone: Boolean = true,
)
