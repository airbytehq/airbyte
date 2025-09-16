package io.airbyte.integrations.source.datagen.flavor.increment

import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.integrations.source.datagen.flavor.DataGenerator
import io.airbyte.integrations.source.datagen.flavor.increment.IncrementFlavor.fields
import io.github.oshai.kotlinlogging.KotlinLogging

class IncrementDataGenerator: DataGenerator {
    private val log = KotlinLogging.logger {}

    override fun generateData(currentID: Long, modulo: Int, offset: Int): NativeRecordPayload {
        val incrementedID = (currentID * modulo + offset)
        val idField = fields["increment"]?.find { it.id == "id" }!!

        val recordData: NativeRecordPayload = mutableMapOf()
        recordData[idField.id] = FieldValueEncoder(
            incrementedID,
            (idField.type as IntegerFieldType).jsonEncoder as JsonEncoder<in Any?>
        )

        return recordData
    }
}
