/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.AirbyteProtocolSchema
import java.util.function.Predicate

/**
 * Verify that the provided JsonNode is a valid AirbyteMessage. Any AirbyteMessage type is allowed
 * (e.g. Record, State, Log, etc).
 */
class AirbyteProtocolPredicate : Predicate<JsonNode?> {
    private val jsonSchemaValidator = JsonSchemaValidator()

    init {
        val schema =
            JsonSchemaValidator.getSchema(AirbyteProtocolSchema.PROTOCOL.file, "AirbyteMessage")
        jsonSchemaValidator.initializeSchemaValidator(PROTOCOL_SCHEMA_NAME, schema)
    }

    override fun test(s: JsonNode?): Boolean {
        return jsonSchemaValidator.testInitializedSchema(PROTOCOL_SCHEMA_NAME, s)
    }

    companion object {
        private const val PROTOCOL_SCHEMA_NAME = "protocol schema"
    }
}
