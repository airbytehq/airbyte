/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.CSVFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.JsonFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.data.toAirbyteValue
import io.airbyte.cdk.load.file.GZIPProcessor
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.test.util.toOutputRecord
import io.airbyte.cdk.load.util.deserializeToNode
import java.io.BufferedReader
import java.io.InputStream
import java.util.zip.GZIPInputStream
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVParser

class ObjectStorageDataDumper(
    private val stream: DestinationStream,
    private val client: ObjectStorageClient<*>,
    private val pathFactory: ObjectStoragePathFactory,
    private val formatConfig: ObjectStorageFormatConfiguration,
    private val compressionConfig: ObjectStorageCompressionConfiguration<*>? = null
) {
    fun dump(): List<OutputRecord> {
        val prefix = pathFactory.getFinalDirectory(stream).toString()
        return runBlocking {
            withContext(Dispatchers.IO) {
                client
                    .list(prefix)
                    .map { listedObject: RemoteObject<*> ->
                        client.get(listedObject.key) { objectData: InputStream ->
                            val reader =
                                when (compressionConfig?.compressor) {
                                    is GZIPProcessor -> GZIPInputStream(objectData)
                                    is NoopProcessor,
                                    null -> objectData
                                    else -> error("Unsupported compressor")
                                }.bufferedReader()
                            readLines(reader)
                        }
                    }
                    .toList()
                    .flatten()
            }
        }
    }

    @Suppress("DEPRECATION")
    private fun readLines(reader: BufferedReader): List<OutputRecord> =
        when (formatConfig) {
            is JsonFormatConfiguration -> {
                reader
                    .lineSequence()
                    .map { line ->
                        line
                            .deserializeToNode()
                            .toAirbyteValue(stream.schemaWithMeta)
                            .toOutputRecord()
                    }
                    .toList()
            }
            is CSVFormatConfiguration -> {
                CSVParser(reader, CSVFormat.DEFAULT.withHeader()).use {
                    it.records.map { record ->
                        record.toAirbyteValue(stream.schemaWithMeta).toOutputRecord()
                    }
                }
            }
            else -> error("Unsupported format")
        }
}
