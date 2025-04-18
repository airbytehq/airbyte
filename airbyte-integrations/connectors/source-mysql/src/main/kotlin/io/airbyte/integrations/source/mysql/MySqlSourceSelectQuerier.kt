/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.SocketConfig
import io.airbyte.cdk.output.SocketOutputFormat
import io.airbyte.cdk.read.JdbcSelectQuerier
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.protocol.AirbyteConfiguredCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

/** Mysql implementation of [JdbcSelectQuerier], which sets fetch size differently */
@Singleton
@Primary
class MySqlSourceSelectQuerier(
    private val jdbcConnectionFactory: JdbcConnectionFactory,
    private val socketConfig: SocketConfig,
) : SelectQuerier by JdbcSelectQuerier(jdbcConnectionFactory, socketConfig) {
    private val log = KotlinLogging.logger {}

    inner class MySqlResult(
        jdbcConnectionFactory: JdbcConnectionFactory,
        q: SelectQuery,
        parameters: SelectQuerier.Parameters,
        cursorQuery: Boolean
    ) : JdbcSelectQuerier.Result(jdbcConnectionFactory, q, parameters,
        if (cursorQuery) { SocketOutputFormat.JSONL } else { socketConfig.outputFormat }) {
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
            parameters.resultSetFetchSize?.let { fetchSize: Int ->
                log.info { "Setting fetchSize to $fetchSize." }
                rs!!.fetchSize = fetchSize
            }
        }
    }   

    override fun executeQuery(
        q: SelectQuery,
        parameters: SelectQuerier.Parameters,
        cursorQuery: Boolean
    ): SelectQuerier.Result = MySqlResult(jdbcConnectionFactory, q, parameters, cursorQuery)
}
