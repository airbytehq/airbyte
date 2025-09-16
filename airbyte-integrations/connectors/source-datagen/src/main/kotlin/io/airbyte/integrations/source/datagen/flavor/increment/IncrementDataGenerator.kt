/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor.increment

import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.integrations.source.datagen.flavor.DataGenerator
import io.airbyte.integrations.source.datagen.flavor.increment.IncrementFlavor.fields

class IncrementDataGenerator : DataGenerator {

    override fun generateData(currentID: Long, modulo: Int, offset: Int): NativeRecordPayload {
        val incrementedID = (currentID * modulo + offset)
        val idField = fields["increment"]?.find { it.id == "id" }!!

        val recordData: NativeRecordPayload = mutableMapOf()
        recordData[idField.id] =
            FieldValueEncoder(
                incrementedID,
                (idField.type as IntegerFieldType).jsonEncoder as LongCodec
            )

        return recordData
    }
}
