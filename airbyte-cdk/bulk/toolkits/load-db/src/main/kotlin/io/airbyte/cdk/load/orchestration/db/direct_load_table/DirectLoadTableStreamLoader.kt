/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.direct_load_table

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader

class DirectLoadTableStreamLoader(
    override val stream: DestinationStream,
    val tableOperations: DirectLoadTableOperations,
) : StreamLoader {
    override suspend fun start() {
        // TODO
        //   * create table if not exists
        //   * alter table if needed
        //   * truncate refresh setup
    }

    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        // TODO
        //   * commit truncate refresh
    }
}
