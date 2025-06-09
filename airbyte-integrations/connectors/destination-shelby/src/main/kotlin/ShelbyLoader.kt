package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.csv.toCsvRecord
import io.airbyte.cdk.load.file.csv.toCsvPrinterWithHeader
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.write.dlq.DlqLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import org.apache.commons.csv.CSVPrinter

private val logger = KotlinLogging.logger {  }

class ShelbyState(private val schema: ObjectType) : AutoCloseable {
    private val outputStream: ByteArrayOutputStream = ByteArrayOutputStream()
    private val printer: CSVPrinter = schema.toCsvPrinterWithHeader(outputStream)
    private val records: MutableList<DestinationRecordRaw> = mutableListOf()

    fun accumulate(record: DestinationRecordRaw) {
        records.add(record)
        printer.printRecord(
            (record.asDestinationRecordAirbyteValue().data as ObjectValue).toCsvRecord(schema)
        )
        printer.flush()
    }

    fun isFull(): Boolean = outputStream.size() > 150

    fun flush(): List<DestinationRecordRaw>? {
        logger.error { "-------- Sending data!" }
        logger.warn { "\n${outputStream}" }
        return null
    }

    override fun close() {}
}

class ShelbyLoader(private val catalog: DestinationCatalog) : DlqLoader<ShelbyState> {
    override fun start(key: StreamKey, part: Int): ShelbyState =
        ShelbyState(
            catalog
                .streams
                .find { it.descriptor == key.stream }
                ?.schema as ObjectType
        )

    override fun accept(record: DestinationRecordRaw, state: ShelbyState): DlqLoader.DlqLoadResult {
        state.accumulate(record)
        if (state.isFull()) {
            val failedRecords = state.flush()
            return DlqLoader.Complete(failedRecords)
        } else {
            return DlqLoader.Incomplete
        }
    }

    override fun finish(state: ShelbyState): DlqLoader.Complete = DlqLoader.Complete(state.flush())

    override fun close() {}
}
