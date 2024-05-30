/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.typing_deduping

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcV1V2Migrator
import io.airbyte.integrations.destination.mysql.MySQLNameTransformer
import java.util.Optional
import lombok.SneakyThrows

class MysqlV1V2Migrator(database: JdbcDatabase) :
    JdbcV1V2Migrator(MySQLNameTransformer(), database, null) {

    @SneakyThrows
    @Throws(Exception::class)
    override fun getTableIfExists(
        namespace: String?,
        tableName: String?
    ): Optional<TableDefinition> {
        return JdbcDestinationHandler.Companion.findExistingTable(
            database,
            // Mysql doesn't have schemas. Pass the namespace as the database name.
            namespace,
            null,
            tableName
        )
    }
}
