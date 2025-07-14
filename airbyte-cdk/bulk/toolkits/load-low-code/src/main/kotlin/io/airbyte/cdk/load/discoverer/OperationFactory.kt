package io.airbyte.cdk.load.discoverer

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.load.command.DestinationOperation
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ObjectType
import io.github.oshai.kotlinlogging.KotlinLogging
import java.lang.IllegalArgumentException

private val logger = KotlinLogging.logger {}

class OperationFactory(
    private val objectNamePath: List<String>,
    private val fieldsPath: List<String>,
    private val fieldFactoriesByImportType: Map<ImportType, FieldFactory>
) {

    /** Generate a destination operation based on a schema object from the API. */
    fun create(schemaFromApi: JsonNode, importType: ImportType): DestinationOperation? {
        val objectName: String = schemaFromApi.extract(objectNamePath).asText()
        val fields = fieldFactoriesByImportType[importType]?.let {
            fieldFactory -> schemaFromApi.extractArray(fieldsPath).map { fieldFactory.create(it) }
        } ?: throw IllegalArgumentException("Unsupported type $importType")

        val matchingKeys =
            fields.filter {
                it.isMatchingKey()
            } // note that composite keys are not supported in this model
        val fieldsForSyncMode = fields.filter { it.isAvailable() }

        if (fieldsForSyncMode.isEmpty()) {
            logger.warn {
                "Object $objectName with operation $importType has no fields and therefore will not be added to the catalog"
            }
            return null
        }
        return DestinationOperation(
            objectName,
            importType,
            getSchema(fieldsForSyncMode),
            matchingKeys.map { listOf(it.getName()) },
        )
    }

    private fun getSchema(
        fieldsForSyncMode: List<Field>,
    ): AirbyteType {
        return ObjectType(
            properties =
                fieldsForSyncMode.associateTo(LinkedHashMap()) { it.getName() to it.getType() },
            additionalProperties = false,
            required = fieldsForSyncMode.filter { it.isRequired() }.map { it.getName() }
        )
    }
}

fun JsonNode.extract(path: List<String>): JsonNode {
    return path.fold(this) { acc, next ->
        acc.get(next) ?: throw IllegalArgumentException("Can't extract field at path: $path")
    }
}

fun JsonNode.extractArray(path: List<String>): ArrayNode {
    val arrayNode = this.extract(path)
    if (arrayNode is ArrayNode) {
        return arrayNode
    }

    throw IllegalArgumentException("Field at path $path is not an array")
}
