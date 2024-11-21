/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3

import io.airbyte.cdk.integrations.destination.record_buffer.BufferCreateFunction
import io.airbyte.cdk.integrations.destination.record_buffer.BufferStorage
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.avro.AvroSerializedBuffer
import io.airbyte.cdk.integrations.destination.s3.avro.UploadAvroFormatConfig
import io.airbyte.cdk.integrations.destination.s3.csv.CsvSerializedBuffer
import io.airbyte.cdk.integrations.destination.s3.csv.UploadCsvFormatConfig
import io.airbyte.cdk.integrations.destination.s3.jsonl.JsonLSerializedBuffer
import io.airbyte.cdk.integrations.destination.s3.jsonl.UploadJsonlFormatConfig
import io.airbyte.cdk.integrations.destination.s3.parquet.ParquetSerializedBuffer
import io.airbyte.commons.json.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.Callable
import java.util.function.Function

private val logger = KotlinLogging.logger {}

class SerializedBufferFactory {

    companion object {
        /**
         * When running a
         * [io.airbyte.cdk.integrations.destination.record_buffer.SerializedBufferingStrategy], it
         * would usually need to instantiate new buffers when flushing data or when it receives data
         * for a brand-new stream. This factory fills this need and @return the function to be
         * called on such events.
         *
         * The factory is responsible for choosing the correct constructor function for a new
         * [SerializableBuffer] that handles the correct serialized format of the data. It is
         * configured by composition with another function to create a new [BufferStorage] where to
         * store it.
         *
         * This factory determines which [UploadFormatConfig] to use depending on the user provided
         * @param config, The @param createStorageFunctionWithoutExtension is the constructor
         * function to call when creating a new buffer where to store data. Note that we typically
         * associate which format is being stored in the storage object thanks to its file
         * extension.
         */
        @JvmStatic
        fun getCreateFunction(
            config: S3DestinationConfig,
            createStorageFunctionWithoutExtension: Function<String, BufferStorage>,
            useV2FieldNames: Boolean = false,
        ): BufferCreateFunction {
            val formatConfig = config.formatConfig!!
            logger.info { "S3 format config: $formatConfig" }
            when (formatConfig.format) {
                FileUploadFormat.AVRO -> {
                    val createStorageFunctionWithExtension = Callable {
                        createStorageFunctionWithoutExtension.apply(
                            formatConfig.fileExtension,
                        )
                    }
                    return AvroSerializedBuffer.createFunction(
                        formatConfig as UploadAvroFormatConfig,
                        createStorageFunctionWithExtension,
                        useV2FieldNames
                    )
                }
                FileUploadFormat.CSV -> {
                    val createStorageFunctionWithExtension = Callable {
                        createStorageFunctionWithoutExtension.apply(
                            formatConfig.fileExtension,
                        )
                    }
                    return CsvSerializedBuffer.createFunction(
                        formatConfig as UploadCsvFormatConfig,
                        createStorageFunctionWithExtension,
                        useV2FieldNames
                    )
                }
                FileUploadFormat.JSONL -> {
                    val createStorageFunctionWithExtension = Callable {
                        createStorageFunctionWithoutExtension.apply(
                            formatConfig.fileExtension,
                        )
                    }
                    return JsonLSerializedBuffer.createBufferFunction(
                        formatConfig as UploadJsonlFormatConfig,
                        createStorageFunctionWithExtension,
                        useV2FieldNames
                    )
                }
                FileUploadFormat.PARQUET -> {
                    // we can't choose the type of buffer storage with parquet because of how the
                    // underlying hadoop
                    // library is imposing file usage.
                    return ParquetSerializedBuffer.createFunction(config, useV2FieldNames)
                }
                else -> {
                    throw RuntimeException("Unexpected output format: ${Jsons.serialize(config)}")
                }
            }
        }
    }
}
