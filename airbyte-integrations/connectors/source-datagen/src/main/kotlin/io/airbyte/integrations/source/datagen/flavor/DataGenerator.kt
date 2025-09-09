package io.airbyte.integrations.source.datagen.flavor

import io.airbyte.cdk.output.sockets.NativeRecordPayload

interface DataGenerator {
    fun generateData(): NativeRecordPayload
    // TODO: add arguments, return statement
}
