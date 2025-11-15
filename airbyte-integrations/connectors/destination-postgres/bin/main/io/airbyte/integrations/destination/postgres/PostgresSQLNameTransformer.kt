/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import java.util.*
import kotlin.math.min

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
        return str.substring(0, min(str.length.toDouble(), 63.0).toInt())
    }
}
