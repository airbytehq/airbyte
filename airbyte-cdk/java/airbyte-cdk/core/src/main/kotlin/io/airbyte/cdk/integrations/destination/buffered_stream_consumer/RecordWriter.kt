/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.buffered_stream_consumer

import io.airbyte.commons.functional.CheckedBiConsumer
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair

fun interface RecordWriter<T> :
    CheckedBiConsumer<AirbyteStreamNameNamespacePair, List<T>, Exception> {
    @Throws(Exception::class)
    override fun accept(stream: AirbyteStreamNameNamespacePair, records: List<T>)
}
