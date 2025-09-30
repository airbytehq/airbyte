/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.operation

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.load.command.DestinationOperation
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.discoverer.destinationobject.DestinationObject
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.decoder.JsonDecoder
import io.airbyte.cdk.load.http.getBodyOrEmpty
import io.airbyte.cdk.load.interpolation.toInterpolationContext
import io.github.oshai.kotlinlogging.KotlinLogging
import java.lang.IllegalArgumentException

private val logger = KotlinLogging.logger {}

/**
 * Create all the DestinationOperations based on a DestinationObject. If properties are not defined
 * in the DestinationObject, this class will require a schemaRequester in order to fetch the
 * properties.
 */
class DestinationOperationAssembler(
    private val propertiesPath: List<String>,
    private val insertionMethods: List<InsertionMethod>,
    private val schemaRequester: HttpRequester?,
) {
    // FIXME once we figure out the decoder interface, we should have this configurable and/or move
    // in a retriever layer. Another trigger to migrate to retriever would be if we need to support
    // pagination
    private val decoder = JsonDecoder()

    fun assemble(destinationObject: DestinationObject): List<DestinationOperation> {
        val apiSchema: JsonNode =
            if (hasProperties(destinationObject.apiRepresentation))
                destinationObject.apiRepresentation
            else
                (schemaRequester
                        ?: throw IllegalStateException(
                            "Object ${destinationObject.name} does not have properties but schemaRequester is not defined to fetch it"
                        ))
                    .send(
                        mapOf(
                            "object" to destinationObject.apiRepresentation.toInterpolationContext()
                        )
                    )
                    .use { response -> decoder.decode(response.getBodyOrEmpty()) }

        if (!hasProperties(apiSchema)) {
            throw IllegalStateException("The schema returned by the API does not have properties")
        }

        return insertionMethods.mapNotNull {
            createOperation(destinationObject.name, apiSchema, it)
        }
    }

    private fun hasProperties(apiObject: JsonNode): Boolean {
        try {
            apiObject.extractArray(propertiesPath)
            return true
        } catch (_: IllegalArgumentException) {
            return false
        }
    }

    /** Generate a destination operation based on a schema object from the API. */
    private fun createOperation(
        objectName: String,
        schemaFromApi: JsonNode,
        insertionMethod: InsertionMethod
    ): DestinationOperation? {
        val properties =
            schemaFromApi.extractArray(propertiesPath).map { insertionMethod.createProperty(it) }
        val matchingKeys =
            properties.filter {
                it.isMatchingKey()
            } // note that composite keys are not supported in this model
        val propertiesForSyncMode = properties.filter { it.isAvailable() }

        if (propertiesForSyncMode.isEmpty()) {
            logger.warn {
                "Object $objectName with operation ${insertionMethod.getImportType()} has no properties and therefore will not be added to the catalog"
            }
            return null
        } else if (insertionMethod.requiresMatchingKey() && matchingKeys.isEmpty()) {
            logger.warn {
                "Object $objectName with operation ${insertionMethod.getImportType()} requires at least one matching key but none was found"
            }
            return null
        }
        return DestinationOperation(
            objectName,
            insertionMethod.getImportType(),
            getSchema(propertiesForSyncMode),
            matchingKeys.map { listOf(it.getName()) },
        )
    }

    private fun getSchema(
        propertiesForSyncMode: List<DiscoveredProperty>,
    ): AirbyteType {
        return ObjectType(
            properties =
                propertiesForSyncMode.associateTo(LinkedHashMap()) { it.getName() to it.getType() },
            additionalProperties = false,
            required = propertiesForSyncMode.filter { it.isRequired() }.map { it.getName() }
        )
    }
}

fun JsonNode.extract(path: List<String>): JsonNode {
    return path.fold(this) { acc, next ->
        acc.get(next) ?: throw IllegalArgumentException("Can't extract property at path: $path")
    }
}

fun JsonNode.extractArray(path: List<String>): ArrayNode {
    val arrayNode = this.extract(path)
    if (arrayNode is ArrayNode) {
        return arrayNode
    }

    throw IllegalArgumentException("property at path $path is not an array")
}
