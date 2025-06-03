package io.airbyte.integrations.destination.shelby.http.job

import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.csv.toCsvRecord
import io.airbyte.cdk.load.file.csv.toCsvPrinterWithHeader
import io.airbyte.cdk.load.message.DestinationRecordRaw
import org.apache.commons.csv.CSVPrinter
import java.io.ByteArrayOutputStream
import org.apache.commons.csv.CSVFormat

const val MAX_SIZE_OF_100_MB: Long = 100 * 1024 * 1024

class Batch(private val schema: ObjectType, private val maxSizeInBytes: Long = MAX_SIZE_OF_100_MB) {
    private val outputStream = ByteArrayOutputStream()
    private val printer: CSVPrinter = schema.toCsvPrinterWithHeader(outputStream, CSVFormat.Builder.create().setRecordSeparator("\n").build())

    fun add(record: DestinationRecordRaw) {
        if (isFull())
            throw IllegalStateException("Can't add records as the batch is already full")
        printer.printRecord((record.asDestinationRecordAirbyteValue().data as ObjectValue).toCsvRecord(schema))  // FIXME we need to format datetime here
        printer.flush()  // FIXME I assume this is not efficient but it is needed for `isFull` to provide the right value and `isFull` is called before adding each records
    }

    fun isFull(): Boolean {
        return outputStream.size() >= maxSizeInBytes
    }

    fun isEmpty(): Boolean {
        return outputStream.size() == 0
    }

    fun toRequestBody(): ByteArray {
        return outputStream.toByteArray()
    }

}
