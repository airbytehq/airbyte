/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import com.google.cloud.bigquery.BigQuery
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.migrations.DirectLoadTableExistenceChecker

class BigqueryDirectLoadTableExistenceChecker(private val bigquery: BigQuery) :
    DirectLoadTableExistenceChecker {
    override fun listExistingTables(tables: Collection<TableName>) =
        tables.filter { tableName ->
            val table = bigquery.getTable(tableName.namespace, tableName.name)
            table != null && table.exists()
        }
}
