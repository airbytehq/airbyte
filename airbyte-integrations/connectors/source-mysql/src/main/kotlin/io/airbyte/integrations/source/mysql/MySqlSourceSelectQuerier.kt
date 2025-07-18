/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.JdbcSelectQuerier
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.SelectQuery
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

/** Mysql implementation of [JdbcSelectQuerier], which sets fetch size differently */
@Singleton
@Primary
class MySqlSourceSelectQuerier(
    jdbcConnectionFactory: JdbcConnectionFactory,
) : SelectQuerier {

    private val wrapped = JdbcSelectQuerier(jdbcConnectionFactory)

    override fun executeQuery(
        q: SelectQuery,
        parameters: SelectQuerier.Parameters,
    ): SelectQuerier.Result {
        val mySqlParameters: SelectQuerier.Parameters =
        // MySQL requires this fetchSize setting on JDBC Statements to enable adaptive fetching.
        // The ResultSet fetchSize value is what's used as an actual hint by the JDBC driver.
        parameters.copy(statementFetchSize = Int.MIN_VALUE)
        return wrapped.executeQuery(q, mySqlParameters)
    }
}
