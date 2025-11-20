/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.model

data class AlterationSummary(
    val added: Map<String, String>,
    val modified: Map<String, String>, // old type -> new type
    val deleted: Set<String>,
    val hasDedupChange: Boolean,
)
/**
 * This indicates if any changes were made to the table, excluding PK changes It indicates that we
 * need to run an alter statement.
 */
fun AlterationSummary.hasApplicableAlterations(): Boolean =
    !(added.isEmpty() && modified.isEmpty() && deleted.isEmpty())
