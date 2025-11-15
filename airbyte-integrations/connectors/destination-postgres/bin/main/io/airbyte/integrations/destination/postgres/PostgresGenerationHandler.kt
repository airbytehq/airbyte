/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.JdbcGenerationHandler

class PostgresGenerationHandler : JdbcGenerationHandler {
    override fun getGenerationIdInTable(
        database: JdbcDatabase,
        namespace: String,
        name: String
    ): Long? {
        val selectTableResultSet =
            database
                .unsafeQuery(
                    """SELECT 1 
            |               FROM pg_catalog.pg_namespace n
            |               JOIN pg_catalog.pg_class c
            |               ON c.relnamespace=n.oid
            |               JOIN pg_catalog.pg_attribute a
            |               ON a.attrelid = c.oid
            |               WHERE n.nspname=?
            |               AND c.relkind='r'
            |               AND c.relname=?
            |               AND a.attname=?
            |               LIMIT 1
        """.trimMargin(),
                    namespace,
                    name,
                    "_airbyte_generation_id"
                )
                .use { it.toList() }
        if (selectTableResultSet.isEmpty()) {
            return null
        } else {
            val selectGenIdResultSet =
                database
                    .unsafeQuery("SELECT _airbyte_generation_id FROM $namespace.$name LIMIT 1;")
                    .use { it.toList() }
            if (selectGenIdResultSet.isEmpty()) {
                return null
            } else {
                val genIdInTable =
                    selectGenIdResultSet.first().get("_airbyte_generation_id")?.asLong()
                LOGGER.info { "found generationId in table $namespace.$name: $genIdInTable" }
                return genIdInTable ?: -1L
            }
        }
    }
}
