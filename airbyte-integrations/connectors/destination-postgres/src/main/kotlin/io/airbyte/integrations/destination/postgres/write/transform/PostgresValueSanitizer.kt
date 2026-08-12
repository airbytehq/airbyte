/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue

internal fun sanitizePostgresValue(value: AirbyteValue): AirbyteValue =
    sanitizePostgresValueWithChange(value).value

private data class SanitizedValue(val value: AirbyteValue, val changed: Boolean)

private fun sanitizePostgresValueWithChange(value: AirbyteValue): SanitizedValue =
    when (value) {
        is StringValue ->
            if ('\u0000' in value.value) {
                SanitizedValue(StringValue(value.value.replace("\u0000", "")), true)
            } else {
                SanitizedValue(value, false)
            }
        is ArrayValue -> {
            var sanitizedValues: MutableList<AirbyteValue>? = null
            value.values.forEachIndexed { index, child ->
                val sanitized = sanitizePostgresValueWithChange(child)
                if (sanitized.changed) {
                    if (sanitizedValues == null) {
                        sanitizedValues = value.values.toMutableList()
                    }
                    sanitizedValues!![index] = sanitized.value
                }
            }
            sanitizedValues?.let { SanitizedValue(ArrayValue(it), true) }
                ?: SanitizedValue(value, false)
        }
        is ObjectValue -> {
            var sanitizedValues: LinkedHashMap<String, AirbyteValue>? = null
            value.values.forEach { (key, child) ->
                val sanitized = sanitizePostgresValueWithChange(child)
                if (sanitized.changed) {
                    if (sanitizedValues == null) {
                        sanitizedValues = LinkedHashMap(value.values)
                    }
                    sanitizedValues!![key] = sanitized.value
                }
            }
            // Nested object keys are intentionally not sanitized; only values are destination data.
            sanitizedValues?.let { SanitizedValue(ObjectValue(it), true) }
                ?: SanitizedValue(value, false)
        }
        else -> SanitizedValue(value, false)
    }
