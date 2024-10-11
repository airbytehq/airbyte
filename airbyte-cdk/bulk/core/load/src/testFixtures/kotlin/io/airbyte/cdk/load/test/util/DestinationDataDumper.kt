/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream

fun interface DestinationDataDumper {
    fun dumpRecords(spec: ConfigurationSpecification, stream: DestinationStream): List<OutputRecord>
}

/**
 * Some integration tests don't need to actually read records from the destination, and can use this
 * implementation to satisfy the compiler.
 */
object FakeDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        throw NotImplementedError()
    }
}
