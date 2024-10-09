/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

fun interface DestinationDataDumper {
    fun dumpRecords(
        streamName: String,
        streamNamespace: String?,
    ): List<OutputRecord>
}

/**
 * Some integration tests don't need to actually read records from the destination, and can use this
 * implementation to satisfy the compiler.
 */
object FakeDataDumper : DestinationDataDumper {
    override fun dumpRecords(streamName: String, streamNamespace: String?): List<OutputRecord> {
        throw NotImplementedError()
    }
}
