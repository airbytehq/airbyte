/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import javax.inject.Singleton

@Singleton
class BigqueryDirectLoaderFactory : DirectLoaderFactory<BigqueryDirectLoader> {
    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int
    ): BigqueryDirectLoader {
        TODO("Not yet implemented")
    }
}

// TODO plug in the ObjectStorageStreamLoader here
//   but also do SQL things???
class BigqueryDirectLoader : DirectLoader {
    override fun accept(record: DestinationRecordAirbyteValue): DirectLoader.DirectLoadResult {
        TODO("Not yet implemented")
    }

    override fun finish() {
        TODO("Not yet implemented")
    }

    override fun close() {
        TODO("Not yet implemented")
    }
}
