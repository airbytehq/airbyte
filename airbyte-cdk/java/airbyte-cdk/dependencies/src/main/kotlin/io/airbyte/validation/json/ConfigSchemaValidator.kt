/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.validation.json

import com.fasterxml.jackson.databind.JsonNode

interface ConfigSchemaValidator<T : Enum<T>> {
    fun validate(configType: T, objectJson: JsonNode): Set<String>?

    fun test(configType: T, objectJson: JsonNode): Boolean

    @Throws(JsonValidationException::class) fun ensure(configType: T, objectJson: JsonNode)

    fun ensureAsRuntime(configType: T, objectJson: JsonNode)
}
