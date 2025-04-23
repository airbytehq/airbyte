/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping

import kotlin.math.max

object TypingDedupingUtil {
    // copied wholesale from old CDK's StreamId
    fun concatenateRawTableName(namespace: String, name: String): String {
        val plainConcat = namespace + name
        // Pretend we always have at least one underscore, so that we never generate
        // `_raw_stream_`
        var longestUnderscoreRun = 1
        var i = 0
        while (i < plainConcat.length) {
            // If we've found an underscore, count the number of consecutive underscores
            var underscoreRun = 0
            while (i < plainConcat.length && plainConcat[i] == '_') {
                underscoreRun++
                i++
            }
            longestUnderscoreRun =
                max(longestUnderscoreRun.toDouble(), underscoreRun.toDouble()).toInt()
            i++
        }

        return namespace + "_raw" + "_".repeat(longestUnderscoreRun + 1) + "stream_" + name
    }
}
