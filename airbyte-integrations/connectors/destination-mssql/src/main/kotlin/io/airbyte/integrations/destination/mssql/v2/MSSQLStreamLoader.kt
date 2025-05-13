/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.StreamStateStore
import javax.sql.DataSource

class MSSQLStreamLoader(
    dataSource: DataSource,
    override val stream: DestinationStream,
    sqlBuilder: MSSQLQueryBuilder,
    private val streamStateStore: StreamStateStore<MSSQLStreamState>
) : AbstractMSSQLStreamLoader(dataSource, stream, sqlBuilder) {

    override suspend fun start() {
        super.start()
        streamStateStore.put(
            stream.descriptor,
            MSSQLDirectLoaderStreamState(dataSource, sqlBuilder)
        )
    }
}
