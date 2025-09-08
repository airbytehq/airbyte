/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import io.airbyte.cdk.load.data.Transformations.Companion.toAlphanumericAndUnderscore
import jakarta.inject.Singleton

@Singleton
class SnowflakeSqlNameTransformer {
    fun transform(name: String): String {
        val normalizedName = toAlphanumericAndUnderscore(name)
        return if (normalizedName.take(1).matches("[A-Za-z_]".toRegex())) {
            normalizedName
        } else {
            "_$normalizedName"
        }
    }
}
