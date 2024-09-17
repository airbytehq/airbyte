/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.mock_integration_test

import io.airbyte.cdk.test.util.DestinationDataDumper
import io.airbyte.cdk.test.util.OutputRecord

object MockDestinationBackend {
    private val lock = Object()
    private val files: MutableMap<String, MutableList<OutputRecord>> = mutableMapOf()

    fun insert(filename: String, vararg records: OutputRecord) {
        synchronized(lock) { getFile(filename).addAll(records) }
    }

    fun readFile(filename: String): List<OutputRecord> {
        return synchronized(lock) {
            getFile(filename)
        }
    }

    private fun getFile(filename: String): MutableList<OutputRecord> {
        return synchronized(lock) {
            if (!files.containsKey(filename)) {
                files[filename] = mutableListOf()
            }
            files[filename]!!
        }
    }
}

object MockDestinationDataDumper : DestinationDataDumper {
    override fun dumpRecords(streamName: String, streamNamespace: String?): List<OutputRecord> {
        return MockDestinationBackend.readFile(
                MockStreamLoader.getFilename(streamNamespace, streamName)
            )
    }
}
