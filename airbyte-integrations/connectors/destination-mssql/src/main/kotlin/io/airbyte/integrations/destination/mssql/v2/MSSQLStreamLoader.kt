/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.StreamCdkStateStore
import javax.sql.DataSource

class MSSQLStreamLoader(
    dataSource: DataSource,
    override val stream: DestinationStream,
    sqlBuilder: MSSQLQueryBuilder,
    private val streamCdkStateStore: StreamCdkStateStore<MSSQLStreamState>
) : AbstractMSSQLStreamLoader(dataSource, stream, sqlBuilder) {

    override suspend fun start() {
        super.start()
        streamCdkStateStore.put(
            stream.mappedDescriptor,
            MSSQLDirectLoaderStreamState(dataSource, sqlBuilder)
        )
    }
}
