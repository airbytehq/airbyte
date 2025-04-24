/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping

import kotlin.math.max

object TypingDedupingUtil {
    fun concatenateRawTableName(namespace: String, name: String): String {
        val plainConcat = namespace + name
        val longestUnderscoreRun =
            Regex("_+")
                .findAll(plainConcat)
                .map { it.value.length }
                .maxOrNull()
                // Pretend we always have at least one underscore, so that we never
                // generate `_raw_stream_`
                .let { max(it ?: 0, 1) }

        val underscores = "_".repeat(longestUnderscoreRun + 1)
        return "${namespace}_raw${underscores}stream_$name"
    }
}
