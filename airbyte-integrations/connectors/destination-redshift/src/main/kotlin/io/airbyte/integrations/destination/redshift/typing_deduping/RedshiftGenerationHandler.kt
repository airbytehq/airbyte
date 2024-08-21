/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.jdbc.JdbcGenerationHandler

class RedshiftGenerationHandler(private val databaseName: String) : JdbcGenerationHandler {
    override fun getGenerationIdInTable(
        database: JdbcDatabase,
        namespace: String,
        name: String
    ): Long? {
        val tableExistsWithGenerationId =
            database.executeMetadataQuery {
                // Find a column named _airbyte_generation_id
                // in the relevant table.
                val resultSet =
                    it.getColumns(
                        databaseName,
                        namespace,
                        name,
                        JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID
                    )
                // Check if there were any such columns.
                resultSet.next()
            }
        // The table doesn't exist, or exists but doesn't have generation id
        if (!tableExistsWithGenerationId) {
            return null
        }

        // The table exists and has generation ID. Query it.
        val queryResult =
            database.queryJsons(
                """
            SELECT ${JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID}
            FROM "$namespace"."$name"
            LIMIT 1
            """.trimIndent()
            )
        return queryResult
            .firstOrNull()
            ?.get(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID)
            ?.asLong()
            ?: 0
    }
}
