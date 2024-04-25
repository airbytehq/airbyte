/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode

interface UploadFormatConfig {
    val format: FileUploadFormat

    val fileExtension: String

    companion object {
        fun withDefault(config: JsonNode, property: String?, defaultValue: String): String {
            val value = config[property]
            if (value == null || value.isNull) {
                return defaultValue
            }
            return value.asText()
        }

        fun withDefault(config: JsonNode, property: String?, defaultValue: Int): Int {
            val value = config[property]
            if (value == null || value.isNull) {
                return defaultValue
            }
            return value.asInt()
        }

        fun withDefault(config: JsonNode, property: String?, defaultValue: Boolean): Boolean {
            val value = config[property]
            if (value == null || value.isNull) {
                return defaultValue
            }
            return value.asBoolean()
        }
    }
}
