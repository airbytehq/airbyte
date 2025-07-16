/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.operation

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.load.command.DestinationOperation
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.discoverer.`object`.DestinationObjectSupplier
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.decoder.JsonDecoder
import io.airbyte.cdk.load.http.getBodyOrEmpty
import io.airbyte.cdk.load.interpolation.toInterpolationContext
import io.github.oshai.kotlinlogging.KotlinLogging
import java.lang.IllegalArgumentException

private val logger = KotlinLogging.logger {}

class DynamicOperationSupplier(
    private val objectsSupplier: DestinationObjectSupplier,
    private val objectNamePath: List<String>,
    private val propertiesPath: List<String>,
    private val propertyFactoriesByImportType: Map<ImportType, PropertyFactory>,
    private val schemaRequester: HttpRequester?,
) : OperationSupplier {
    // FIXME once we figure out the decoder interface, we should have this configurable and/or move in a retriever layer
    private val decoder = JsonDecoder()

    override fun get(): List<DestinationOperation> {
        return objectsSupplier.get().flatMap {
            val apiSchema: JsonNode =
                if (hasProperties(it.apiRepresentation)) it.apiRepresentation
                else
                    schemaRequester
                        ?.send(mapOf("object" to it.apiRepresentation.toInterpolationContext()))
                        ?.use { response -> decoder.decode(response.getBodyOrEmpty()) }
                        ?: throw IllegalStateException("Object ${it.name} does not have properties but schemaRequester is not defined to fetch it")
            propertyFactoriesByImportType.mapNotNull { (importType, propertyFactory) ->
                createOperation(
                    it.apiRepresentation.extract(objectNamePath).asText(),
                    apiSchema,
                    importType,
                    propertyFactory
                )
            }
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
        importType: ImportType,
        propertyFactory: PropertyFactory
    ): DestinationOperation? {
        val properties =
            schemaFromApi.extractArray(propertiesPath).map { propertyFactory.create(it) }
        val matchingKeys =
            properties.filter {
                it.isMatchingKey()
            } // note that composite keys are not supported in this model
        val propertiesForSyncMode = properties.filter { it.isAvailable() }

        if (propertiesForSyncMode.isEmpty()) {
            logger.warn {
                "Object $objectName with operation $importType has no properties and therefore will not be added to the catalog"
            }
            return null
        }
        return DestinationOperation(
            objectName,
            importType,
            getSchema(propertiesForSyncMode),
            matchingKeys.map { listOf(it.getName()) },
        )
    }

    private fun getSchema(
        propertiesForSyncMode: List<Property>,
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
