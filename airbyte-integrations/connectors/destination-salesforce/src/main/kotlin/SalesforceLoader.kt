/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce

import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.csv.toCsvRecord
import io.airbyte.cdk.load.file.csv.toCsvPrinterWithHeader
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.dlq.newDlqRecord
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.write.dlq.DlqLoader
import io.airbyte.integrations.destination.salesforce.io.airbyte.integrations.destination.salesforce.http.job.JobRepository
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter

private val logger = KotlinLogging.logger {}

const val MAX_SIZE_OF_100_MB: Long = 100 * 1024 * 1024

class SalesforceState(
    private val jobRepository: JobRepository,
    private val stream: DestinationStream,
    private val maxSizeInBytes: Long = MAX_SIZE_OF_100_MB
) : AutoCloseable {
    private val outputStream: ByteArrayOutputStream = ByteArrayOutputStream()
    private val schema: ObjectType = stream.schema as ObjectType
    private val printer: CSVPrinter =
        schema.toCsvPrinterWithHeader(
            outputStream,
            CSVFormat.Builder.create().setRecordSeparator("\n").build()
        )
    private val mapper: ObjectMapper = ObjectMapper()

    fun accumulate(record: DestinationRecordRaw) {
        if (isFull()) {
            throw IllegalStateException("Can't add records as the batch is already full")
        }

        printer.printRecord(
            (record.asDestinationRecordAirbyteValue().data as ObjectValue).toCsvRecord(schema)
        )
        printer.flush() // this is not efficient but it is needed for `isFull` to provide the right
        // value and `isFull` is called before adding each records
    }

    fun isFull(): Boolean = outputStream.size() >= maxSizeInBytes

    fun flush(): List<DestinationRecordRaw>? {
        logger.info { "Pushing data for stream ${stream.mappedDescriptor.toPrettyString()}" }
        val job = jobRepository.create(stream, outputStream.toByteArray())
        jobRepository.startIngestion(job)
        logger.info {
            "Stream ${stream.mappedDescriptor.toPrettyString()} - Starting ingestion for job ${job.id}"
        }
        while (true) {
            jobRepository.updateStatus(job)
            if (job.status.isTerminal()) {
                logger.info {
                    "Stream ${stream.mappedDescriptor.toPrettyString()} - Job ${job.id} completed with status ${job.status}"
                }
                break
            }
            Thread.sleep(5000)
        }

        return jobRepository.fetchFailedRecords(job).map { stream.newDlqRecord(it) }
    }

    override fun close() {}
}

class SalesforceLoader(
    private val jobRepository: JobRepository,
    private val catalog: DestinationCatalog
) : DlqLoader<SalesforceState> {
    override fun start(key: StreamKey, part: Int): SalesforceState {
        logger.info { "SalesforceLoader.start for ${key.serializeToString()} with part $part" }
        return SalesforceState(
            jobRepository,
            catalog.streams.find { it.mappedDescriptor == key.stream }
                ?: throw IllegalStateException(
                    "Could not find stream ${key.stream} as part of the catalog."
                )
        )
    }

    override fun accept(
        record: DestinationRecordRaw,
        state: SalesforceState
    ): DlqLoader.DlqLoadResult {
        state.accumulate(record)
        if (state.isFull()) {
            val failedRecords = state.flush()
            return DlqLoader.Complete(failedRecords)
        } else {
            return DlqLoader.Incomplete
        }
    }

    override fun finish(state: SalesforceState): DlqLoader.Complete =
        DlqLoader.Complete(state.flush())

    override fun close() {}
}
