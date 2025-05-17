package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

class ShelbyLoader : DirectLoader {

    private val records = mutableListOf<DestinationRecordRaw>()
    override fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        records.add(record)
        if (records.size >= 5)
            return DirectLoader.Complete
        else
            return DirectLoader.Incomplete
    }

    override fun finish() {
        KotlinLogging.logger {  }.error { "Finished (NOOP)" }
    }

    override fun close() {
        KotlinLogging.logger {  }.error { "Sending with ${records.size} records: $records" }
    }
}

@Singleton
class ShelbyLoaderFactory: DirectLoaderFactory<ShelbyLoader> {
    override fun create(streamDescriptor: DestinationStream.Descriptor, part: Int): ShelbyLoader {
        KotlinLogging.logger {  }.error { "Creating a ShelbyLoader for $streamDescriptor $part" }
        return ShelbyLoader()
    }
}
