/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables

import com.google.cloud.bigquery.BigQuery
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.migrations.DirectLoadTableExistenceChecker
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.toTableId

class BigqueryDirectLoadTableExistenceChecker(private val bigquery: BigQuery) :
    DirectLoadTableExistenceChecker {
    override fun listExistingTables(tables: Collection<TableName>): Collection<TableName> =
        tables.filter { bigquery.getTable(it.toTableId()) != null }
}
