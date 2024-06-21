/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.formatter

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.QueryParameterValue
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.json.Jsons.emptyObject
import io.airbyte.commons.json.Jsons.serialize
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import java.util.*
import java.util.concurrent.TimeUnit

/**
 * The class formats incoming JsonSchema and AirbyteRecord in order to be inline with a
 * corresponding uploader.
 */
class BigQueryRecordFormatter {
    fun formatRecord(recordMessage: PartialAirbyteMessage, generationId: Long): String {
        val record = emptyObject() as ObjectNode
        record.put(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, UUID.randomUUID().toString())
        record.put(
            JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
            getEmittedAtField(recordMessage.record)
        )
        record.set<JsonNode>(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT, NullNode.instance)
        record.put(JavaBaseConstants.COLUMN_NAME_DATA, recordMessage.serialized)
        record.put(
            JavaBaseConstants.COLUMN_NAME_AB_META,
            Jsons.serialize<AirbyteRecordMessageMeta>(recordMessage.record!!.meta!!)
        )
        record.put(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID, generationId)
        return serialize(record)
    }

    private fun getEmittedAtField(recordMessage: PartialAirbyteRecordMessage?): String? {
        // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds
        // then
        // use BQ helpers to string-format correctly.
        val emittedAtMicroseconds =
            TimeUnit.MICROSECONDS.convert(recordMessage!!.emittedAt, TimeUnit.MILLISECONDS)
        return QueryParameterValue.timestamp(emittedAtMicroseconds).value
    }

    companion object {
        val SCHEMA_V2: Schema =
            Schema.of(
                Field.of(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, StandardSQLTypeName.STRING),
                Field.of(
                    JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
                    StandardSQLTypeName.TIMESTAMP
                ),
                Field.of(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT, StandardSQLTypeName.TIMESTAMP),
                Field.of(JavaBaseConstants.COLUMN_NAME_DATA, StandardSQLTypeName.STRING),
                Field.of(JavaBaseConstants.COLUMN_NAME_AB_META, StandardSQLTypeName.STRING),
                Field.of(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID, StandardSQLTypeName.INT64)
            )
    }
}
