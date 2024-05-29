/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.csv

import io.airbyte.cdk.integrations.destination.record_buffer.BaseSerializedBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.BufferCreateFunction
import io.airbyte.cdk.integrations.destination.record_buffer.BufferStorage
import io.airbyte.cdk.integrations.destination.s3.util.CompressionType
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.io.OutputStream
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.util.UUID
import java.util.concurrent.Callable
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter
import org.apache.commons.csv.QuoteMode
import org.apache.commons.lang3.StringUtils

private val logger = KotlinLogging.logger {}

class CsvSerializedBuffer(
    bufferStorage: BufferStorage,
    private val csvSheetGenerator: CsvSheetGenerator,
    compression: Boolean
) : BaseSerializedBuffer(bufferStorage) {
    private var csvPrinter: CSVPrinter? = null
    private var csvFormat: CSVFormat

    init {
        csvFormat = CSVFormat.DEFAULT
        // we always want to compress csv files
        withCompression(compression)
    }

    fun withCsvFormat(csvFormat: CSVFormat): CsvSerializedBuffer {
        if (csvPrinter == null) {
            this.csvFormat = csvFormat
            return this
        }
        throw RuntimeException("Options should be configured before starting to write")
    }

    @Throws(IOException::class)
    override fun initWriter(outputStream: OutputStream) {
        csvPrinter = CSVPrinter(PrintWriter(outputStream, true, StandardCharsets.UTF_8), csvFormat)
    }

    /**
     * TODO: (ryankfu) remove this call within
     * [io.airbyte.cdk.integrations.destination.record_buffer.SerializedBufferingStrategy] and move
     * to use recordString
     *
     * @param record AirbyteRecordMessage to be written
     * @throws IOException
     */
    @Deprecated("Deprecated in Java")
    @Throws(IOException::class)
    override fun writeRecord(record: AirbyteRecordMessage) {
        csvPrinter!!.printRecord(csvSheetGenerator.getDataRow(UUID.randomUUID(), record))
    }

    @Throws(IOException::class)
    override fun writeRecord(recordString: String, airbyteMetaString: String, emittedAt: Long) {
        csvPrinter!!.printRecord(
            csvSheetGenerator.getDataRow(
                UUID.randomUUID(),
                recordString,
                emittedAt,
                airbyteMetaString,
            ),
        )
    }

    @Throws(IOException::class)
    override fun flushWriter() {
        // in an async world, it is possible that flush writer gets called even if no records were
        // accepted.
        if (csvPrinter != null) {
            csvPrinter!!.flush()
        } else {
            logger.warn { "Trying to flush but no printer is initialized." }
        }
    }

    @Throws(IOException::class)
    override fun closeWriter() {
        // in an async world, it is possible that flush writer gets called even if no records were
        // accepted.
        if (csvPrinter != null) {
            csvPrinter!!.close()
        } else {
            logger.warn { "Trying to close but no printer is initialized." }
        }
    }

    companion object {

        const val CSV_GZ_SUFFIX: String = ".csv.gz"

        @JvmStatic
        @Suppress("DEPRECATION")
        fun createFunction(
            config: UploadCsvFormatConfig?,
            createStorageFunction: Callable<BufferStorage>
        ): BufferCreateFunction {
            return BufferCreateFunction {
                stream: AirbyteStreamNameNamespacePair,
                catalog: ConfiguredAirbyteCatalog ->
                if (config == null) {
                    return@BufferCreateFunction CsvSerializedBuffer(
                        createStorageFunction.call(),
                        StagingDatabaseCsvSheetGenerator(),
                        true,
                    )
                }
                val csvSheetGenerator =
                    CsvSheetGenerator.Factory.create(
                        catalog.streams
                            .filter { s: ConfiguredAirbyteStream ->
                                s.stream.name == stream.name &&
                                    StringUtils.equals(
                                        s.stream.namespace,
                                        stream.namespace,
                                    )
                            }
                            .firstOrNull()
                            ?.stream
                            ?.jsonSchema
                            ?: throw RuntimeException(
                                String.format(
                                    "No such stream %s.%s",
                                    stream.namespace,
                                    stream.name,
                                ),
                            ),
                        config,
                    )
                val csvSettings =
                    CSVFormat.DEFAULT.withQuoteMode(QuoteMode.NON_NUMERIC)
                        .withHeader(*csvSheetGenerator.getHeaderRow().toTypedArray<String>())
                val compression = config.compressionType != CompressionType.NO_COMPRESSION
                CsvSerializedBuffer(
                        createStorageFunction.call(),
                        csvSheetGenerator,
                        compression,
                    )
                    .withCsvFormat(csvSettings)
            }
        }
    }
}
