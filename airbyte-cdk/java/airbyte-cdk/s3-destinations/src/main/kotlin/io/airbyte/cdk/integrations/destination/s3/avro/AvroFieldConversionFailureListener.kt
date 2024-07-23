/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.avro

import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.lang.Exception
import org.apache.avro.Schema
import org.apache.avro.SchemaBuilder
import org.apache.avro.generic.GenericData
import org.apache.avro.generic.GenericRecordBuilder
import tech.allegro.schema.json2avro.converter.FieldConversionFailureListener

class AvroFieldConversionFailureListener : FieldConversionFailureListener() {
    val CHANGE_SCHEMA: Schema =
        SchemaBuilder.builder()
            .record("change")
            .fields()
            .name("field")
            .type()
            .stringType()
            .noDefault()
            .name("change")
            .type()
            .stringType()
            .noDefault()
            .name("reason")
            .type()
            .stringType()
            .noDefault()
            .endRecord()

    override fun onFieldConversionFailure(
        avroName: String,
        originalName: String,
        schema: Schema,
        value: Any,
        path: String,
        exception: Exception
    ): Any? {

        pushPostProcessingAction { record ->
            val change: GenericData.Record =
                GenericRecordBuilder(CHANGE_SCHEMA)
                    .set("field", originalName)
                    .set("change", AirbyteRecordMessageMetaChange.Change.NULLED.value()!!)
                    .set(
                        "reason",
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
                            .value()!!
                    )
                    .build()
            val meta = record.get("_airbyte_meta") as GenericData.Record
            @Suppress("UNCHECKED_CAST")
            val changes = meta.get("changes") as? MutableList<GenericData.Record>
            changes?.add(change)
            record
        }

        return null
    }
}
