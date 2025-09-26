/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor.increment

import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.integrations.source.datagen.flavor.DataGenerator

class IncrementDataGenerator() : DataGenerator {

    override fun generateData(currentID: Long, modulo: Int, offset: Int): NativeRecordPayload {
        val incrementedID = (currentID * modulo + offset)
        val recordData: NativeRecordPayload = mutableMapOf()

        recordData["id"] = FieldValueEncoder(
            incrementedID,
            IntegerFieldType.jsonEncoder as LongCodec
        )

        recordData["boolean"] = FieldValueEncoder(
            incrementedID % 2 == 1L,
            BooleanFieldType.jsonEncoder as BooleanCodec
        )

        recordData["string"] = FieldValueEncoder(
            "string$incrementedID",
            StringFieldType.jsonEncoder as TextCodec
        )

        return recordData
    }
}
