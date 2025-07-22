/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.skeleton_directload.write.typing_deduping.direct_load_tables

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadSqlGenerator

class SkeletonDirectLoadSqlGenerator : DirectLoadSqlGenerator {
    override fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ): Sql {
        return Sql.of(
            """
            // This does not do anything but it should create a table
            """.trimIndent()
        )
    }

    override fun overwriteTable(sourceTableName: TableName, targetTableName: TableName): Sql {
        return Sql.of(
            """
            // This does not do anything but it should overwrite a table
            """.trimIndent()
        )
    }

    override fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): Sql {
        return Sql.of(
            """
            // This does not do anything but it should copy a table
            """.trimIndent()
        )
    }

    override fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): Sql {
        return Sql.of(
            """
            // This does not do anything but it should copy a table
            """.trimIndent()
        )
    }

    override fun dropTable(tableName: TableName): Sql {
        return Sql.of(
            """
            // This does not do anything but it should drop a table
            """.trimIndent()
        )
    }
}
