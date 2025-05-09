/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables

import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.migrations.DirectLoadTableExistenceChecker

class BigqueryDirectLoadTableExistenceChecker : DirectLoadTableExistenceChecker {
    override fun listExistingTables(tables: Collection<TableName>): Collection<TableName> {
        TODO("Not yet implemented")
    }
}
