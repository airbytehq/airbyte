/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.buffered_stream_consumer

import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair

fun interface CheckAndRemoveRecordWriter {
    /**
     * Compares the name of the current staging file with the method argument. If the names are
     * different, then the staging writer corresponding to `stagingFileName` is closed and the name
     * of the new file where the record will be sent will be returned.
     */
    @Throws(Exception::class)
    fun apply(stream: AirbyteStreamNameNamespacePair, stagingFileName: String?): String?
}
