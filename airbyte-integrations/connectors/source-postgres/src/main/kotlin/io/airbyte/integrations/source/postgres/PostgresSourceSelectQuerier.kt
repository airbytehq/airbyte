/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.SelectQuery

// @Singleton
// @Primary
class PostgresSourceSelectQuerier(jdbcConnectionFactory: JdbcConnectionFactory) : SelectQuerier {
    override fun executeQuery(
        q: SelectQuery,
        parameters: SelectQuerier.Parameters
    ): SelectQuerier.Result {
        TODO("Not yet implemented")
    }
}
