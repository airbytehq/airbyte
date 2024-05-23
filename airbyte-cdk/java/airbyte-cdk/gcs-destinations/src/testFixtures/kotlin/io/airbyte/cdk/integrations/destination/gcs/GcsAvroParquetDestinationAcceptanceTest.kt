/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.avro.JsonSchemaType
import io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.NumberDataTypeTestArgumentProvider
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import java.io.IOException
import java.util.*
import java.util.function.Function
import java.util.stream.Collectors
import java.util.stream.StreamSupport
import org.apache.avro.Schema
import org.apache.avro.generic.GenericData
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ArgumentsSource

abstract class GcsAvroParquetDestinationAcceptanceTest(fileUploadFormat: FileUploadFormat) :
    GcsDestinationAcceptanceTest(fileUploadFormat) {
    override fun getProtocolVersion() = ProtocolVersion.V1

    @ParameterizedTest
    @ArgumentsSource(NumberDataTypeTestArgumentProvider::class)
    @Throws(Exception::class)
    fun testNumberDataType(catalogFileName: String, messagesFileName: String) {
        val catalog = readCatalogFromFile(catalogFileName)
        val messages = readMessagesFromFile(messagesFileName)

        val config = this.getConfig()
        val defaultSchema = getDefaultSchema(config)
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false)

        for (stream in catalog.streams) {
            val streamName = stream.name
            val schema = if (stream.namespace != null) stream.namespace else defaultSchema!!

            val actualSchemaTypes = retrieveDataTypesFromPersistedFiles(streamName, schema)
            val expectedSchemaTypes = retrieveExpectedDataTypes(stream)

            Assertions.assertEquals(expectedSchemaTypes, actualSchemaTypes)
        }
    }

    private fun retrieveExpectedDataTypes(stream: AirbyteStream): Map<String, Set<Schema.Type>> {
        val iterableNames = Iterable { stream.jsonSchema["properties"].fieldNames() }
        val nameToNode =
            StreamSupport.stream(iterableNames.spliterator(), false)
                .collect(
                    Collectors.toMap(
                        Function.identity(),
                        Function { name: String -> getJsonNode(stream, name) }
                    )
                )

        return nameToNode.entries.associate { it.key to getExpectedSchemaType(it.value) }
    }

    private fun getJsonNode(stream: AirbyteStream, name: String): JsonNode {
        val properties = stream.jsonSchema["properties"]
        if (properties.size() == 1) {
            return properties["data"]
        }
        return properties[name]["items"]
    }

    private fun getExpectedSchemaType(fieldDefinition: JsonNode): Set<Schema.Type> {
        // The $ref is a migration to V1 data type protocol see well_known_types.yaml
        val typeProperty =
            if (fieldDefinition["type"] == null) fieldDefinition["\$ref"]
            else fieldDefinition["type"]
        val airbyteTypeProperty = fieldDefinition["airbyte_type"]
        val airbyteTypePropertyText = airbyteTypeProperty?.asText()
        return JsonSchemaType.entries
            .toTypedArray()
            .filter { value: JsonSchemaType ->
                value.jsonSchemaType == typeProperty.asText() &&
                    compareAirbyteTypes(airbyteTypePropertyText, value)
            }
            .map { it.avroType }
            .toSet()
    }

    private fun compareAirbyteTypes(
        airbyteTypePropertyText: String?,
        value: JsonSchemaType
    ): Boolean {
        if (airbyteTypePropertyText == null) {
            return value.jsonSchemaAirbyteType == null
        }
        return airbyteTypePropertyText == value.jsonSchemaAirbyteType
    }

    @Throws(IOException::class)
    private fun readCatalogFromFile(catalogFilename: String): AirbyteCatalog {
        return Jsons.deserialize(
            MoreResources.readResource(catalogFilename),
            AirbyteCatalog::class.java
        )
    }

    @Throws(IOException::class)
    private fun readMessagesFromFile(messagesFilename: String): List<AirbyteMessage> {
        return MoreResources.readResource(messagesFilename).lines().map {
            Jsons.deserialize(it, AirbyteMessage::class.java)
        }
    }

    @Throws(Exception::class)
    protected abstract fun retrieveDataTypesFromPersistedFiles(
        streamName: String,
        namespace: String
    ): Map<String?, Set<Schema.Type?>?>

    protected fun getTypes(record: GenericData.Record): Map<String, Set<Schema.Type>> {
        val fieldList =
            record.schema.fields.filter { field: Schema.Field ->
                !field.name().startsWith("_airbyte")
            }

        return if (fieldList.size == 1) {
            fieldList.associate {
                it.name() to
                    it.schema()
                        .types
                        .map { obj: Schema -> obj.type }
                        .filter { type: Schema.Type -> type != Schema.Type.NULL }
                        .toSet()
            }
        } else {
            fieldList.associate {
                it.name() to
                    it.schema()
                        .types
                        .filter { type: Schema -> type.type != Schema.Type.NULL }
                        .flatMap { type: Schema -> type.elementType.types }
                        .map { obj: Schema -> obj.type }
                        .filter { type: Schema.Type -> type != Schema.Type.NULL }
                        .toSet()
            }
        }
    }
}
