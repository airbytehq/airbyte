/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor.increment

import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.integrations.source.datagen.flavor.DataGenerator

class IncrementDataGenerator() : DataGenerator {
    val stringData = "string".repeat(200)

    override fun generateData(currentID: Long, modulo: Int, offset: Int): NativeRecordPayload {
        val incrementedID = (currentID * modulo + offset)
        val recordData: NativeRecordPayload = mutableMapOf()

        recordData["id"] =
            FieldValueEncoder(incrementedID, IntegerFieldType.jsonEncoder as LongCodec)

        recordData["string"] =
            FieldValueEncoder("$incrementedID$stringData", StringFieldType.jsonEncoder as TextCodec)

        return recordData
    }
}
