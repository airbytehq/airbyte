/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

import io.airbyte.commons.functional.CheckedBiConsumer
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair

fun interface FlushBufferFunction :
    CheckedBiConsumer<AirbyteStreamNameNamespacePair, SerializableBuffer, Exception> {
    @Throws(Exception::class)
    override fun accept(stream: AirbyteStreamNameNamespacePair, buffer: SerializableBuffer)
}
