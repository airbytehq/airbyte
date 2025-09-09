package io.airbyte.integrations.source.datagen.flavor.increment

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.integrations.source.datagen.flavor.DataGenerator
import io.airbyte.integrations.source.datagen.flavor.increment.IncrementFlavor.fields
import io.airbyte.protocol.models.v0.AirbyteRecordMessage

class IncrementDataGenerator: DataGenerator {
    private var currentID = 0

    override fun generateData(): NativeRecordPayload {
        val incrementedID = ++currentID
        val idField = fields["increment"]?.find { it.id == "id" }!!

        val recordData: NativeRecordPayload = mutableMapOf()
        recordData[idField.id] = FieldValueEncoder(
            incrementedID.toLong(),
            (idField.type as IntegerFieldType).jsonEncoder as JsonEncoder<in Any?>
        )

        return recordData
    }
}
