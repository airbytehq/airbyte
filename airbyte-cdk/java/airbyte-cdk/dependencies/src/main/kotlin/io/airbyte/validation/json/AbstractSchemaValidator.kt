/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.validation.json

import com.fasterxml.jackson.databind.JsonNode
import java.nio.file.Path

abstract class AbstractSchemaValidator<T : Enum<T>>
@JvmOverloads
constructor(private val jsonSchemaValidator: JsonSchemaValidator = JsonSchemaValidator()) :
    ConfigSchemaValidator<T> {
    abstract fun getSchemaPath(configType: T): Path

    private fun getSchemaJson(configType: T): JsonNode {
        return JsonSchemaValidator.Companion.getSchema(getSchemaPath(configType).toFile())
    }

    override fun validate(configType: T, objectJson: JsonNode): Set<String>? {
        return jsonSchemaValidator.validate(getSchemaJson(configType), objectJson)
    }

    override fun test(configType: T, objectJson: JsonNode): Boolean {
        return jsonSchemaValidator.test(getSchemaJson(configType), objectJson)
    }

    @Throws(JsonValidationException::class)
    override fun ensure(configType: T, objectJson: JsonNode) {
        jsonSchemaValidator.ensure(getSchemaJson(configType), objectJson)
    }

    override fun ensureAsRuntime(configType: T, objectJson: JsonNode) {
        jsonSchemaValidator.ensureAsRuntime(getSchemaJson(configType), objectJson)
    }
}
