/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import java.util.*

class SnowflakeSQLNameTransformer : StandardNameTransformer() {
    override fun applyDefaultCase(input: String): String {
        return input.uppercase(Locale.getDefault())
    }

    /** The first character can only be alphanumeric or an underscore. */
    override fun convertStreamName(input: String): String {
        val normalizedName = super.convertStreamName(input)
        return if (normalizedName.substring(0, 1).matches("[A-Za-z_]".toRegex())) {
            normalizedName
        } else {
            "_$normalizedName"
        }
    }
}
