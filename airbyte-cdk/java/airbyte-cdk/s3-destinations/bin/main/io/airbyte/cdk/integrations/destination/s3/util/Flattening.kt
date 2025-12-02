/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.util

import com.fasterxml.jackson.annotation.JsonCreator
import kotlin.jvm.Throws

enum class Flattening(val value: String) {
    NO("No flattening"),
    ROOT_LEVEL("Root level flattening");

    companion object {
        @JvmStatic
        @JsonCreator
        @Throws(IllegalArgumentException::class)
        fun fromValue(value: String): Flattening {
            for (f in entries) {
                if (f.value.equals(value, ignoreCase = true)) {
                    return f
                }
            }
            throw IllegalArgumentException("Unexpected value: $value")
        }
    }
}
