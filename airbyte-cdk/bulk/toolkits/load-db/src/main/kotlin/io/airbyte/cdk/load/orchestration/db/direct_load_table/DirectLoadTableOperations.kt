/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.direct_load_table

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.DestinationHandler
import io.airbyte.cdk.load.orchestration.db.TableName

class DirectLoadTableOperations(
    private val sqlGenerator: DirectLoadSqlGenerator,
    private val destinationHandler: DestinationHandler,
) {
    fun createTable(
        stream: DestinationStream,
        finalTableName: TableName,
        suffix: String,
        replace: Boolean
    ) {
        destinationHandler.execute(TODO())
    }

    fun alterTable(
        stream: DestinationStream,
        finalTableName: TableName,
    ) {
        // TODO we should figure out some reasonable abstraction for diffing existing+expected
        //  table schema
        TODO()
    }

    fun overwriteFinalTable(
        finalTableName: TableName,
        suffix: String,
    ) {
        TODO()
    }
}
