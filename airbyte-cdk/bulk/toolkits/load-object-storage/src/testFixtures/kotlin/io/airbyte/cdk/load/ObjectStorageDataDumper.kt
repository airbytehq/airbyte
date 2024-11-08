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
import io.airbyte.cdk.load.data.avro.AvroMapperPipelineFactory
import io.airbyte.cdk.load.data.avro.toAirbyteValue
import io.airbyte.cdk.load.data.avro.toAvroSchema
import io.airbyte.cdk.load.data.csv.toAirbyteValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.data.parquet.ParquetMapperPipelineFactory
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.GZIPProcessor
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.avro.toAvroReader
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.parquet.toParquetReader
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.test.util.maybeUnflatten
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
    private val avroMapperPipeline = AvroMapperPipelineFactory().create(stream)
    private val parquetMapperPipeline = ParquetMapperPipelineFactory().create(stream)

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
                            .toAirbyteValue(stream.schema.withAirbyteMeta(wasFlattened))
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
                val finalSchema = avroMapperPipeline.finalSchema.withAirbyteMeta(wasFlattened)
                inputStream.toAvroReader(finalSchema.toAvroSchema(stream.descriptor)).use { reader
                    ->
                    reader
                        .recordSequence()
                        .map {
                            it.toAirbyteValue(finalSchema)
                                .maybeUnflatten(wasFlattened)
                                .toOutputRecord()
                        }
                        .toList()
                }
            }
            is ParquetFormatConfiguration -> {
                val finalSchema = parquetMapperPipeline.finalSchema.withAirbyteMeta(wasFlattened)
                inputStream.toParquetReader(finalSchema.toAvroSchema(stream.descriptor)).use {
                    reader ->
                    reader
                        .recordSequence()
                        .map {
                            it.toAirbyteValue(finalSchema)
                                .maybeUnflatten(wasFlattened)
                                .toOutputRecord()
                        }
                        .toList()
                }
            }
        }
    }
}
