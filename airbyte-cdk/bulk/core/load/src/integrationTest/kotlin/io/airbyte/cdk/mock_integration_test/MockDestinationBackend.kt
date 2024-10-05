/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.mock_integration_test

import io.airbyte.cdk.test.util.DestinationDataDumper
import io.airbyte.cdk.test.util.OutputRecord
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
    override fun dumpRecords(streamName: String, streamNamespace: String?): List<OutputRecord> {
        return MockDestinationBackend.readFile(
            MockStreamLoader.getFilename(streamNamespace, streamName)
        )
    }
}
