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
import io.airbyte.cdk.load.data.csv.toAirbyteValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.GZIPProcessor
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.avro.toAvroReader
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.parquet.toParquetReader
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState.Companion.OPTIONAL_ORDINAL_SUFFIX_PATTERN
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.test.util.maybeUnflatten
import io.airbyte.cdk.load.test.util.toOutputRecord
import io.airbyte.cdk.load.util.deserializeToNode
import java.io.BufferedReader
import java.io.InputStream
import java.util.zip.GZIPInputStream
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.filter
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
        // Note: this is implicitly a test of the `streamConstant` final directory
        // and the path matcher, so a failure here might imply a bug in the metadata-based
        // destination state loader, which lists by `prefix` and filters against the matcher.
        val prefix = pathFactory.getLongestStreamConstantPrefix(stream)
        val matcher =
            pathFactory.getPathMatcher(stream, suffixPattern = OPTIONAL_ORDINAL_SUFFIX_PATTERN)
        return runBlocking {
            withContext(Dispatchers.IO) {
                client
                    .list(prefix)
                    .filter { matcher.match(it.key) != null }
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

    fun dumpFile(): List<String> {
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
                            BufferedReader(decompressed.reader()).readText()
                        }
                    }
                    .toList()
            }
        }
    }

    @Suppress("DEPRECATION")
    private fun readLines(inputStream: InputStream): List<OutputRecord> {
        val wasFlattened = formatConfig.rootLevelFlattening
        return when (formatConfig) {
            is JsonFormatConfiguration -> {
                inputStream
                    .bufferedReader()
                    .lineSequence()
                    .map { line ->
                        line
                            .deserializeToNode()
                            .toAirbyteValue()
                            .maybeUnflatten(wasFlattened)
                            .toOutputRecord()
                    }
                    .toList()
            }
            is CSVFormatConfiguration -> {
                CSVParser(inputStream.bufferedReader(), CSVFormat.DEFAULT.withHeader()).use {
                    it.records.map { record ->
                        record
                            .toAirbyteValue(stream.schema.withAirbyteMeta(wasFlattened))
                            .maybeUnflatten(wasFlattened)
                            .toOutputRecord()
                    }
                }
            }
            is AvroFormatConfiguration -> {
                inputStream.toAvroReader(stream.descriptor).use { reader ->
                    reader
                        .recordSequence()
                        .map { it.toAirbyteValue().maybeUnflatten(wasFlattened).toOutputRecord() }
                        .toList()
                }
            }
            is ParquetFormatConfiguration -> {
                inputStream.toParquetReader(stream.descriptor).use { reader ->
                    reader
                        .recordSequence()
                        .map { it.toAirbyteValue().maybeUnflatten(wasFlattened).toOutputRecord() }
                        .toList()
                }
            }
        }
    }
}
