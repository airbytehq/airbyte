/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.hubspot.http

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.util.Jsons
import java.io.InputStream

class HubSpotCustomObjectSchemaResponseBuilder {
    private val response = Jsons.objectNode()
    private val results = response.putArray("results")

    fun withResult(
        builder: HubSpotSchemaResponseBuilder
    ): HubSpotCustomObjectSchemaResponseBuilder {
        results.add(builder.schema)
        return this
    }

    fun build(): InputStream {
        return ObjectMapper().writeValueAsString(response).byteInputStream()
    }
}

class HubSpotSchemaResponseBuilder {
    internal val schema = Jsons.objectNode()
    private val properties = schema.putArray("properties")

    init {
        this.withName("any_object_name")
    }

    fun withName(name: String): HubSpotSchemaResponseBuilder {
        schema.put("name", name)
        return this
    }

    fun withProperty(
        property: HubSpotPropertySchemaBuilder,
    ): HubSpotSchemaResponseBuilder {
        properties.add(property.build())
        return this
    }

    fun build(): InputStream {
        return ObjectMapper().writeValueAsString(schema).byteInputStream()
    }
}

class HubSpotPropertySchemaBuilder {
    private val node = Jsons.objectNode().apply { this.putObject("modificationMetadata") }

    init {
        this.withName("any_name").withType("string").withCalculated(false).withReadOnlyValue(false)
    }

    fun withCalculated(calculated: Boolean): HubSpotPropertySchemaBuilder {
        node.put("calculated", calculated)
        return this
    }

    fun withName(name: String): HubSpotPropertySchemaBuilder {
        node.put("name", name)
        return this
    }

    fun withType(type: String): HubSpotPropertySchemaBuilder {
        node.put("type", type)
        return this
    }

    fun withReadOnlyValue(readOnlyValue: Boolean): HubSpotPropertySchemaBuilder {
        (node.get("modificationMetadata") as ObjectNode).put("readOnlyValue", readOnlyValue)
        return this
    }

    fun build(): ObjectNode {
        return node
    }
}
