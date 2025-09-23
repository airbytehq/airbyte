package io.airbyte.integrations.source.datagen.flavor

import io.airbyte.cdk.output.sockets.NativeRecordPayload

interface DataGenerator {
    fun generateData(currentID: Long, modulo: Int, offset: Int): NativeRecordPayload
}
