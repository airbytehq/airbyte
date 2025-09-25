/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor.increment

import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.integrations.source.datagen.BooleanFieldType
import io.airbyte.integrations.source.datagen.IntegerFieldType
import io.airbyte.integrations.source.datagen.StringFieldType
import io.airbyte.integrations.source.datagen.flavor.DataGenerator

class IncrementDataGenerator(val requestedSchema: List<Field>) : DataGenerator {

    override fun generateData(currentID: Long, modulo: Int, offset: Int): NativeRecordPayload {
        val incrementedID = (currentID * modulo + offset)
        val recordData: NativeRecordPayload = mutableMapOf()

        for (field in requestedSchema) {
            val value =
                when (field.type) {
                    is BooleanFieldType ->
                        FieldValueEncoder(
                            incrementedID % 2 == 1L,
                            (field.type as BooleanFieldType).jsonEncoder as BooleanCodec
                        )
                    is StringFieldType ->
                        FieldValueEncoder(
                            "string$incrementedID",
                            (field.type as StringFieldType).jsonEncoder as TextCodec
                        )
                    is IntegerFieldType ->
                        FieldValueEncoder(
                            incrementedID,
                            (field.type as IntegerFieldType).jsonEncoder as LongCodec
                        )
                    else -> throw RuntimeException("Unsupported type: ${field.type}")
                }
            recordData[field.id] = value
        }
        return recordData
    }
}
