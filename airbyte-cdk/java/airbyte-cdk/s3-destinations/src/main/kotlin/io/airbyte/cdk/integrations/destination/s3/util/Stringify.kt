/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.util

import com.fasterxml.jackson.annotation.JsonCreator
import kotlin.jvm.Throws

enum class Stringify(val value: String) {
    NO("Default"),
    STRINGIFY("Stringify");

    companion object {
        @JvmStatic
        @JsonCreator
        @Throws(IllegalArgumentException::class)
        fun fromValue(value: String): Stringify {
            for (s in entries) {
                if (s.value.equals(value, ignoreCase = true)) {
                    return s
                }
            }
            throw IllegalArgumentException("Unexpected value: $value")
        }
    }
}
