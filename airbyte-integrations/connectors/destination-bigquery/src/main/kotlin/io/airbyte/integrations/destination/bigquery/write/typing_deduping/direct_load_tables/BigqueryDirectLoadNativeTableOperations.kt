/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.QueryJobConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations

class BigqueryDirectLoadNativeTableOperations(private val bigquery: BigQuery) :
    DirectLoadTableNativeOperations {
    override fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        TODO("Not yet implemented")
    }

    override fun getGenerationId(tableName: TableName): Long {
        val result =
            bigquery.query(
                QueryJobConfiguration.of(
                    "SELECT _airbyte_generation_id FROM ${tableName.namespace}.${tableName.name}$ LIMIT 1"
                ),
            )
        val value = result.iterateAll().first().get(Meta.COLUMN_NAME_AB_GENERATION_ID)
        return if (value.isNull) {
            0
        } else {
            value.longValue
        }
    }
}
