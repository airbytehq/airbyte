/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping

data class TypingDedupingExecutionConfig(
    val rawTableSuffix: String,
)
