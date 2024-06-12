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
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.UUID
import org.apache.avro.Schema
import org.apache.avro.generic.GenericData
import tech.allegro.schema.json2avro.converter.JsonAvroConverter

class AvroRecordFactory(private val schema: Schema?, private val converter: JsonAvroConverter?) {

    companion object {
        private val MAPPER: ObjectMapper = MoreMappers.initMapper()
        private val WRITER: ObjectWriter = MAPPER.writer()
    }

    @Throws(JsonProcessingException::class)
    fun getAvroRecord(id: UUID, recordMessage: AirbyteRecordMessage): GenericData.Record {
        val jsonRecord = MAPPER.createObjectNode()
        jsonRecord.put(JavaBaseConstants.COLUMN_NAME_AB_ID, id.toString())
        jsonRecord.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.emittedAt)
        jsonRecord.setAll<JsonNode>(recordMessage.data as ObjectNode)

        return converter!!.convertToGenericDataRecord(WRITER.writeValueAsBytes(jsonRecord), schema)
    }

    @Throws(JsonProcessingException::class)
    fun getAvroRecord(formattedData: JsonNode?): GenericData.Record {
        val bytes = WRITER.writeValueAsBytes(formattedData)
        return converter!!.convertToGenericDataRecord(bytes, schema)
    }
}
