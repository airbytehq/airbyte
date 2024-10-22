/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.JdbcGenerationHandler

class RedshiftGenerationHandler(private val databaseName: String) : JdbcGenerationHandler {
    override fun getGenerationIdInTable(
        database: JdbcDatabase,
        namespace: String,
        name: String
    ): Long? {
        // for now, just use 0. this means we will always use a temp final table.
        // platform has a workaround for this, so it's OK.
        // TODO only fetch this on truncate syncs
        // TODO once we have destination state, use that instead of a query
        return 0
    }
}
