/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadSqlGenerator

class BigqueryDirectLoadSqlGenerator : DirectLoadSqlGenerator {
    override fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ): Sql {
        TODO("Not yet implemented")
    }

    override fun overwriteTable(sourceTableName: TableName, targetTableName: TableName): Sql {
        TODO("Not yet implemented")
    }

    override fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): Sql {
        TODO("Not yet implemented")
    }

    override fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): Sql {
        TODO("Not yet implemented")
    }

    override fun dropTable(tableName: TableName): Sql {
        TODO("Not yet implemented")
    }
}
