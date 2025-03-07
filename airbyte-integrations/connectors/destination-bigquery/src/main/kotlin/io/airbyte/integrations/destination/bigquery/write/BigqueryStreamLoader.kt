/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.bigquery.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.TableNames

class BigqueryStreamLoader(
    override val stream: DestinationStream,
    config: BigqueryConfiguration,
    tableNames: TableNames,
) : StreamLoader {
    override suspend fun start() {
        super.start()
        // TODO create raw+final table if not exists
        //   ... truncate refresh nonsense
        // see AbstractStreamOperation.init
        // also - CatalogParser's column name collision nonsense. Let's build
        // map<canonical column name -> actual destination column name> ?
    }

    override suspend fun close(streamFailure: StreamProcessingFailed?) {
        super.close(streamFailure)
        // TODO execute T+D
        //   ... more truncate refresh nonsense
        // AbstractStreamOperation.finalizeTable
    }
}
