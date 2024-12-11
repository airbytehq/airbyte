/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.JdbcSelectQuerier
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.SelectQuery
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

/** Mysql implementation of [JdbcSelectQuerier], which sets fetch size differently */
@Singleton
@Primary
class MysqlSelectQuerier(
    private val jdbcConnectionFactory: JdbcConnectionFactory,
) : SelectQuerier by JdbcSelectQuerier(jdbcConnectionFactory) {
    private val log = KotlinLogging.logger {}

    override fun executeQuery(
        q: SelectQuery,
        parameters: SelectQuerier.Parameters,
    ): SelectQuerier.Result = MysqlResult(jdbcConnectionFactory, q, parameters)

    inner class MysqlResult(
        jdbcConnectionFactory: JdbcConnectionFactory,
        q: SelectQuery,
        parameters: SelectQuerier.Parameters,
    ) : JdbcSelectQuerier.Result(jdbcConnectionFactory, q, parameters) {
        /**
         * Mysql does things differently with fetch size. Setting fetch size on a result set is
         * safer than on a statement.
         */
        override fun initQueryExecution() {
            conn = jdbcConnectionFactory.get()
            stmt = conn!!.prepareStatement(q.sql)
            stmt!!.fetchSize = Int.MIN_VALUE
            var paramIdx = 1
            for (binding in q.bindings) {
                log.info { "Setting parameter #$paramIdx to $binding." }
                binding.type.set(stmt!!, paramIdx, binding.value)
                paramIdx++
            }
            rs = stmt!!.executeQuery()
            parameters.fetchSize?.let { fetchSize: Int ->
                log.info { "Setting fetchSize to $fetchSize." }
                rs!!.fetchSize = fetchSize
            }
        }
    }
}
