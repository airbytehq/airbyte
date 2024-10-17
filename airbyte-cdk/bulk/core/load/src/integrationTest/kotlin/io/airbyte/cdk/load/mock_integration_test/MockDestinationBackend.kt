/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

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

    fun retainNewRecords(filename: String, minGenerationId: Long) {
        getFile(filename).removeAll {
            it.generationId == null || it.generationId!! < minGenerationId
        }
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
