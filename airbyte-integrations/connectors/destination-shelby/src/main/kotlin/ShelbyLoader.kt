package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.csv.toCsvRecord
import io.airbyte.cdk.load.file.csv.toCsvPrinterWithHeader
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import org.apache.commons.csv.CSVPrinter

class ShelbyLoader : DirectLoader {

    // This wouldn't be nullable if we could inject the stream schema
    private val outputStream = ByteArrayOutputStream()
    private var printer: CSVPrinter? = null
    private var count = 0
    override fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        val schema = (record.schema as? ObjectType) ?: throw IllegalArgumentException("schema isn't on ObjectType")
        if (printer == null) {
            printer = schema.toCsvPrinterWithHeader(outputStream)
        }
        printer?.let { csvPrinter: CSVPrinter ->
            count += 1
            csvPrinter.printRecord((record.asDestinationRecordAirbyteValue().data as ObjectValue).toCsvRecord(schema))
            csvPrinter.flush()
            if (outputStream.size() > 100)
                return DirectLoader.Complete
            else
                return DirectLoader.Incomplete
        } ?: throw IllegalArgumentException("csvPrinter is null")
    }

    override fun finish() {
        KotlinLogging.logger {  }.error { "Finished (NOOP)" }
    }

    override fun close() {
        printer?.let { csvPrinter ->
            csvPrinter.close()
            KotlinLogging.logger {  }.error { "Sending with $count records" }
            KotlinLogging.logger {  }.warn { "\n$outputStream" }
        }
    }
}

@Singleton
class ShelbyLoaderFactory: DirectLoaderFactory<ShelbyLoader> {
    override fun create(streamDescriptor: DestinationStream.Descriptor, part: Int): ShelbyLoader {
        KotlinLogging.logger {  }.error { "Creating a ShelbyLoader for $streamDescriptor $part" }
        return ShelbyLoader()
    }
}
