/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.model

data class AlterationSummary(
    val added: Map<String, String>,
    val modified: Map<String, String>, // old type -> new type
    val deleted: Set<String>
)

fun AlterationSummary.isEmpty(): Boolean =
    added.isEmpty() && modified.isEmpty() && deleted.isEmpty()
