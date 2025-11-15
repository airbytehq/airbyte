/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.util

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.s3.avro.JsonFieldNameUpdater
import io.airbyte.cdk.integrations.destination.s3.avro.JsonToAvroSchemaConverter
import io.airbyte.commons.util.MoreIterators

/**
 * Helper methods for unit tests. This is needed by multiple modules, so it is in the src directory.
 */
object AvroRecordHelper {
    @JvmStatic
    fun getFieldNameUpdater(
        streamName: String,
        namespace: String?,
        streamSchema: JsonNode
    ): JsonFieldNameUpdater {
        val schemaConverter = JsonToAvroSchemaConverter()
        schemaConverter.getAvroSchema(streamSchema, streamName, namespace)
        return JsonFieldNameUpdater(schemaConverter.getStandardizedNames())
    }

    /**
     * Convert an Airbyte JsonNode from Avro / Parquet Record to a plain one.
     *
     * * Remove the airbyte id and emission timestamp fields.
     * * Remove null fields that must exist in Parquet but does not in original Json. This function
     * mutates the input Json.
     */
    @JvmStatic
    fun pruneAirbyteJson(input: JsonNode): JsonNode {
        val output = input as ObjectNode

        // Remove Airbyte columns.
        output.remove(JavaBaseConstants.COLUMN_NAME_AB_ID)
        output.remove(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)

        // Fields with null values does not exist in the original Json but only in Parquet.
        for (field in MoreIterators.toList(output.fieldNames())) {
            if (output[field] == null || output[field].isNull) {
                output.remove(field)
            }
        }

        return output
    }
}
