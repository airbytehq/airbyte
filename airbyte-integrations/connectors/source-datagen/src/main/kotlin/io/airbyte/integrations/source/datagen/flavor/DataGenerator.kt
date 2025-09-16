/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor

import io.airbyte.cdk.output.sockets.NativeRecordPayload

interface DataGenerator {
    fun generateData(currentID: Long, modulo: Int, offset: Int): NativeRecordPayload
}
