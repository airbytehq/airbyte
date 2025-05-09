/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog

class BigqueryDirectLoadDatabaseInitialStateGatherer :
    DatabaseInitialStatusGatherer<DirectLoadInitialStatus> {
    override suspend fun gatherInitialStatus(
        streams: TableCatalog
    ): Map<DestinationStream, DirectLoadInitialStatus> {
        TODO("Not yet implemented")
    }
}
