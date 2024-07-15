/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.util

import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.s3.avro.AvroConstants
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.avro.LogicalTypes
import org.apache.avro.Schema
import org.apache.avro.SchemaBuilder

private val LOGGER = KotlinLogging.logger {}

object GcsUtils {

    private val UUID_SCHEMA: Schema =
        LogicalTypes.uuid().addToSchema(Schema.create(Schema.Type.STRING))
    private val TIMESTAMP_MILLIS_SCHEMA: Schema =
        LogicalTypes.timestampMillis().addToSchema(Schema.create(Schema.Type.LONG))
    private val NULLABLE_TIMESTAMP_MILLIS: Schema =
        SchemaBuilder.builder().unionOf().nullType().and().type(TIMESTAMP_MILLIS_SCHEMA).endUnion()

    fun getDefaultAvroSchema(
        name: String,
        namespace: String,
        appendAirbyteFields: Boolean,
        useDestinationsV2Columns: Boolean
    ): Schema? {
        LOGGER.info { "Default schema." }
        val stdName = AvroConstants.NAME_TRANSFORMER.getIdentifier(name)
        val stdNamespace = AvroConstants.NAME_TRANSFORMER.getNamespace(namespace)
        var builder = SchemaBuilder.record(stdName).namespace(stdNamespace)
        if (useDestinationsV2Columns) {
            builder.namespace("airbyte")
        }

        var assembler = builder.fields()
        if (useDestinationsV2Columns) {
            if (appendAirbyteFields) {
                assembler =
                    assembler
                        .name(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID)
                        .type(UUID_SCHEMA)
                        .noDefault()
                assembler =
                    assembler
                        .name(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT)
                        .type(TIMESTAMP_MILLIS_SCHEMA)
                        .noDefault()
                assembler =
                    assembler
                        .name(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT)
                        .type(NULLABLE_TIMESTAMP_MILLIS)
                        .withDefault(null)
            }
        } else {
            if (appendAirbyteFields) {
                assembler =
                    assembler
                        .name(JavaBaseConstants.COLUMN_NAME_AB_ID)
                        .type(UUID_SCHEMA)
                        .noDefault()
                assembler =
                    assembler
                        .name(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)
                        .type(TIMESTAMP_MILLIS_SCHEMA)
                        .noDefault()
            }
        }
        assembler =
            assembler.name(JavaBaseConstants.COLUMN_NAME_DATA).type().stringType().noDefault()

        return assembler.endRecord()
    }
}
