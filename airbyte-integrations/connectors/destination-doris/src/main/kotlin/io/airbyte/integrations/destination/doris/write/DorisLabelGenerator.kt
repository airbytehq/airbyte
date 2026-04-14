/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.write

import java.util.UUID
import java.util.regex.Pattern

/**
 * Generates unique labels for Doris Stream Load requests. Labels provide idempotency: if the same
 * label is submitted twice, Doris rejects the duplicate.
 *
 * Format: airbyte_{table}_{uuid} Retry format: airbyte_{table}_{uuid}_retry{N}
 */
object DorisLabelGenerator {

    private val LABEL_PATTERN = Pattern.compile("^[-_A-Za-z0-9]{1,128}$")
    private const val PREFIX = "airbyte"

    fun generateLabel(table: String): String {
        val uuid = UUID.randomUUID().toString().replace("-", "")
        val sanitized = table.replace(Regex("[^A-Za-z0-9_]"), "_")
        val label = "${PREFIX}_${sanitized}_$uuid"

        return if (LABEL_PATTERN.matcher(label).matches() && label.length <= 128) {
            label
        } else {
            // Fallback if table name makes label too long
            "${PREFIX}_$uuid"
        }
    }

    fun retryLabel(originalLabel: String, retryCount: Int): String {
        return "${originalLabel}_r$retryCount"
    }
}
