/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.fusion

import com.fasterxml.jackson.databind.JsonNode

/** Extract the original configured catalog without a dependency on either CDK's stream model. */
object FusionSchema {
    @JvmStatic
    fun fromConfiguredStream(configuredStream: JsonNode): Map<String, Any?> {
        val sourceSchema = configuredStream.path("stream").get("json_schema")
        require(sourceSchema != null && !sourceSchema.isNull) {
            "Configured stream must contain stream.json_schema"
        }
        val primaryKey = configuredStream.get("primary_key")
        val cursor = configuredStream.get("cursor_field")
        require(primaryKey == null || primaryKey.isNull || primaryKey.isArray) {
            "Configured stream primary_key must be an array"
        }
        require(cursor == null || cursor.isNull || cursor.isArray) {
            "Configured stream cursor_field must be an array"
        }
        return mapOf(
            "source_schema" to sourceSchema,
            "primary_key" to primaryKey?.takeUnless { it.isNull }?.toList().orEmpty(),
            "cursor" to cursor?.takeUnless { it.isNull }?.toList().orEmpty(),
        )
    }
}
