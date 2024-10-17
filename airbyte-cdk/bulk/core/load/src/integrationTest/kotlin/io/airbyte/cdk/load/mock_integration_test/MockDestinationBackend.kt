/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import java.util.concurrent.ConcurrentHashMap

object MockDestinationBackend {
    private val files: MutableMap<String, MutableList<OutputRecord>> = ConcurrentHashMap()

    fun insert(filename: String, vararg records: OutputRecord) {
        getFile(filename).addAll(records)
    }

    fun readFile(filename: String): List<OutputRecord> {
        return getFile(filename)
    }

    private fun getFile(filename: String): MutableList<OutputRecord> {
        return files.getOrPut(filename) { mutableListOf() }
    }
}

object MockDestinationDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        return MockDestinationBackend.readFile(
            MockStreamLoader.getFilename(stream.descriptor.namespace, stream.descriptor.name)
        )
    }
}
