/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.AvroFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.CSVFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.JsonFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ParquetFormatConfiguration
import io.airbyte.cdk.load.data.avro.toAirbyteValue
import io.airbyte.cdk.load.data.avro.toAvroSchema
import io.airbyte.cdk.load.data.csv.toAirbyteValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.file.GZIPProcessor
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.avro.toAvroReader
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.parquet.toParquetReader
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.test.util.toOutputRecord
import io.airbyte.cdk.load.util.deserializeToNode
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
                            val decompressed =
                                when (compressionConfig?.compressor) {
                                    is GZIPProcessor -> GZIPInputStream(objectData)
                                    is NoopProcessor,
                                    null -> objectData
                                    else -> error("Unsupported compressor")
                                }
                            readLines(decompressed)
                        }
                    }
                    .toList()
                    .flatten()
            }
        }
    }

    @Suppress("DEPRECATION")
    private fun readLines(inputStream: InputStream): List<OutputRecord> =
        when (formatConfig) {
            is JsonFormatConfiguration -> {
                inputStream
                    .bufferedReader()
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
                CSVParser(inputStream.bufferedReader(), CSVFormat.DEFAULT.withHeader()).use {
                    it.records.map { record ->
                        record.toAirbyteValue(stream.schemaWithMeta).toOutputRecord()
                    }
                }
            }
            is AvroFormatConfiguration -> {
                inputStream
                    .toAvroReader(stream.schemaWithMeta.toAvroSchema(stream.descriptor))
                    .use { reader ->
                        reader
                            .recordSequence()
                            .map { it.toAirbyteValue(stream.schemaWithMeta).toOutputRecord() }
                            .toList()
                    }
            }
            is ParquetFormatConfiguration -> {
                inputStream
                    .toParquetReader(stream.schemaWithMeta.toAvroSchema(stream.descriptor))
                    .use { reader ->
                        reader
                            .recordSequence()
                            .map { it.toAirbyteValue(stream.schemaWithMeta).toOutputRecord() }
                            .toList()
                    }
            }
        }
}
