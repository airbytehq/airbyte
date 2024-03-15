/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import org.jooq.Configuration
import org.jooq.DSLContext
import org.jooq.impl.DSL
import java.sql.SQLException

/**
 * Database object for interacting with a Jooq connection.
 */
open class Database(private val dslContext: DSLContext) {
    @Throws(SQLException::class)
    open fun <T> query(transform: ContextQueryFunction<T>): T? {
        return transform.query(dslContext)
    }

    @Throws(SQLException::class)
    open fun <T> transaction(transform: ContextQueryFunction<T>): T? {
        return dslContext.transactionResult { configuration: Configuration? -> transform.query(DSL.using(configuration)) }
    }
}
