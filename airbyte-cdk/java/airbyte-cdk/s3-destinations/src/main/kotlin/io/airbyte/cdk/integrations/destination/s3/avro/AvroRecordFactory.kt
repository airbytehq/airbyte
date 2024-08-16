/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.core.JsonProcessingException
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.ObjectWriter
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.s3.avro.AvroConstants.Companion.AVRO_EXTRA_PROPS_FIELD
import io.airbyte.cdk.integrations.destination.s3.avro.AvroConstants.Companion.JSON_EXTRA_PROPS_FIELDS
import io.airbyte.cdk.integrations.destination.s3.avro.AvroConstants.Companion.NAME_TRANSFORMER
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.UUID
import org.apache.avro.Schema
import org.apache.avro.generic.GenericData
import tech.allegro.schema.json2avro.converter.JsonAvroConverter

class AvroRecordFactory(
    private val schema: Schema?,
    private val converter: JsonAvroConverter?,
    private val recordPreprocessor: ((JsonNode) -> JsonNode?) = { it }
) {

    companion object {
        private val MAPPER: ObjectMapper = MoreMappers.initMapper()
        private val WRITER: ObjectWriter = MAPPER.writer()

        fun createV1JsonToAvroConverter(): JsonAvroConverter {
            return JsonAvroConverter.builder()
                .setNameTransformer { name: String ->
                    NAME_TRANSFORMER.getIdentifier(
                        name,
                    )
                }
                .setJsonAdditionalPropsFieldNames(JSON_EXTRA_PROPS_FIELDS)
                .setAvroAdditionalPropsFieldName(AVRO_EXTRA_PROPS_FIELD)
                .build()
        }

        fun createV2JsonToAvroConverter(): JsonAvroConverter {
            return JsonAvroConverter.builder()
                .setNameTransformer { name: String ->
                    NAME_TRANSFORMER.getIdentifier(
                        name,
                    )
                }
                .setFieldConversionFailureListener(AvroFieldConversionFailureListener())
                .build()
        }
    }

    @Throws(JsonProcessingException::class)
    fun getAvroRecord(id: UUID, recordMessage: AirbyteRecordMessage): GenericData.Record {
        val jsonRecord = MAPPER.createObjectNode()
        jsonRecord.put(JavaBaseConstants.COLUMN_NAME_AB_ID, id.toString())
        jsonRecord.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.emittedAt)
        jsonRecord.setAll<JsonNode>(recordMessage.data as ObjectNode)

        return converter!!.convertToGenericDataRecord(WRITER.writeValueAsBytes(jsonRecord), schema)
    }

    fun getAvroRecordV2(
        id: UUID,
        generationId: Long,
        syncId: Long,
        recordMessage: AirbyteRecordMessage
    ): GenericData.Record {
        val jsonRecord = MAPPER.createObjectNode()
        jsonRecord.put(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, id.toString())
        jsonRecord.put(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, recordMessage.emittedAt)
        jsonRecord.put(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID, generationId)
        val meta = MAPPER.valueToTree(recordMessage.meta) as ObjectNode
        meta.put("sync_id", syncId)
        jsonRecord.replace(JavaBaseConstants.COLUMN_NAME_AB_META, meta)

        // Preprocess the client data to add features not supported by the converter
        val data = recordMessage.data as ObjectNode
        val preprocessed = recordPreprocessor.invoke(data)
        jsonRecord.setAll<JsonNode>(preprocessed as ObjectNode)

        return converter!!.convertToGenericDataRecord(WRITER.writeValueAsBytes(jsonRecord), schema)
    }

    @Throws(JsonProcessingException::class)
    fun getAvroRecord(formattedData: JsonNode?): GenericData.Record {
        val bytes = WRITER.writeValueAsBytes(formattedData)
        return converter!!.convertToGenericDataRecord(bytes, schema)
    }
}
