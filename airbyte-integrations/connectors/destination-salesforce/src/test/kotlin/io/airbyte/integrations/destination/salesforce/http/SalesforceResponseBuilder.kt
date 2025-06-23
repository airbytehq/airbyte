/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce.http

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.util.Jsons
import java.io.InputStream

class SalesforceSObjectsResponseBuilder {
    private val sobjects = mutableListOf<ObjectNode>()

    fun withObject(
        name: String,
    ): SalesforceSObjectsResponseBuilder {
        val sobject = Jsons.objectNode().apply { put("name", name) }
        sobjects.add(sobject)
        return this
    }

    fun build(): InputStream {
        val response =
            Jsons.objectNode().apply { putArray("sobjects").apply { sobjects.forEach { add(it) } } }
        return ObjectMapper().writeValueAsString(response).byteInputStream()
    }
}

class SalesforceFieldBuilder {
    private val response =
        Jsons.objectNode().apply {
            put("name", "any-name")
            put("type", "string")
            put("createable", false)
            put("updateable", false)
            put("nillable", false)
            put("defaultedOnCreate", false)
            put("externalId", false)
        }

    fun withName(name: String): SalesforceFieldBuilder {
        response.put("name", name)
        return this
    }

    fun withType(type: String): SalesforceFieldBuilder {
        response.put("type", type)
        return this
    }

    fun withCreateable(createable: Boolean): SalesforceFieldBuilder {
        response.put("createable", createable)
        return this
    }

    fun withUpdateable(updateable: Boolean): SalesforceFieldBuilder {
        response.put("updateable", updateable)
        return this
    }

    fun withNillable(nillable: Boolean): SalesforceFieldBuilder {
        response.put("nillable", nillable)
        return this
    }

    fun withDefaultedOnCreate(defaultedOnCreate: Boolean): SalesforceFieldBuilder {
        response.put("defaultedOnCreate", defaultedOnCreate)
        return this
    }

    fun withExternalId(externalId: Boolean): SalesforceFieldBuilder {
        response.put("externalId", externalId)
        return this
    }

    fun build(): ObjectNode {
        return response
    }
}

class SalesforceSObjectDescribeResponseBuilder {
    private val response =
        Jsons.objectNode().apply {
            put("name", "any-name")
            put("createable", false)
            put("deletable", false)
            put("updateable", false)
            putArray("fields")
        }

    fun withName(name: String): SalesforceSObjectDescribeResponseBuilder {
        response.apply { put("name", name) }
        return this
    }

    fun withCreateable(createable: Boolean): SalesforceSObjectDescribeResponseBuilder {
        response.apply { put("createable", createable) }
        return this
    }

    fun withUpdateable(updateable: Boolean): SalesforceSObjectDescribeResponseBuilder {
        response.apply { put("updateable", updateable) }
        return this
    }

    fun withDeletable(deletable: Boolean): SalesforceSObjectDescribeResponseBuilder {
        response.apply { put("deletable", deletable) }
        return this
    }

    fun withField(fieldBuilder: SalesforceFieldBuilder): SalesforceSObjectDescribeResponseBuilder {
        (response.get("fields") as ArrayNode).add(fieldBuilder.build())
        return this
    }

    fun build(): InputStream {
        return ObjectMapper().writeValueAsString(response).byteInputStream()
    }
}
