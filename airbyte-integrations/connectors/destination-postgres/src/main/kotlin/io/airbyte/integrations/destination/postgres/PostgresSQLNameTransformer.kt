/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import java.util.*
import kotlin.math.min
import kotlin.math.abs

class PostgresSQLNameTransformer : StandardNameTransformer() {
    // I _think_ overriding these two methods is sufficient to apply the truncation logic everywhere
    // but this interface + our superclass are weirdly complicated, so plausibly something is
    // missing
    override fun getIdentifier(name: String): String {
        return truncate(super.getIdentifier(name))
    }

    override fun convertStreamName(input: String): String {
        return truncate(super.convertStreamName(input))
    }

    override fun applyDefaultCase(input: String): String {
        return input.lowercase(Locale.getDefault())
    }

    // see https://github.com/airbytehq/airbyte/issues/35333
    // We cannot delete these method until connectors don't need old v1 raw table references for
    // migration
    @Deprecated("") // Overriding a deprecated method is, itself, a warning
    @Suppress("deprecation")
    override fun getRawTableName(streamName: String): String {
        return convertStreamName("_airbyte_raw_" + streamName.lowercase(Locale.getDefault()))
    }

    /**
     * Postgres silently truncates identifiers to 63 characters. Utility method to do that
     * truncation explicitly, so that we can detect e.g. name collisions.
     */
    private fun truncate(str: String): String {
        /*
            V2 Now uses {rawTableName}_airbyte_tmp, but never checks the length of the full string.
            Truncating the rawTableName to 63 leaves no room for this crazy long suffix name (why is it not _tmp??)
            I've put this hack in for 2 purposes. First, anything longer than 60 gets truncated down and has a base36 hashcode
            applied based on the untruncated string for deterministic uniquness. This still will cause `_airbyte_tmp` to get truncated
            because nothing checks the length of that string (appears to be built deeper in the CDK), but that seems to be okay since everything
            before that point is already unique. I'd also suggest shortening the suffix this to something like _tmp,
            which will always fit with the algorithm below since we leave 4 characters for suffixes.
        */

        return if (str.length >= 60.0) str.substring(0, min(str.length.toDouble(), 52.0).toInt()).plus(abs(str.hashCode()).toString(36)) else str
    }
}
