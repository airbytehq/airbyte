/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.read.JdbcSelectQuerier
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.SelectQuery
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import javax.inject.Singleton

private val log = KotlinLogging.logger {}

@Singleton
@Primary
class MysqlJdbcSelectQuerier(val base: JdbcSelectQuerier) : SelectQuerier by base {

    override fun executeQuery(
        q: SelectQuery,
        parameters: SelectQuerier.Parameters
    ): SelectQuerier.Result {
        log.info { "Executing query: ${q.sql}" }
        return base.executeQuery(q, SelectQuerier.Parameters(fetchSize = Int.MIN_VALUE))
    }
}
