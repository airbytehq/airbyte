/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import java.sql.SQLException
import org.jooq.Configuration
import org.jooq.DSLContext
import org.jooq.impl.DSL

/** Database object for interacting with a Jooq connection. */
open class Database(protected val dslContext: DSLContext) {
    @Throws(SQLException::class)
    open fun <T> query(transform: ContextQueryFunction<T>): T {
        return transform.query(dslContext)
    }

    @Throws(SQLException::class)
    open fun <T> transaction(transform: ContextQueryFunction<T>): T? {
        return dslContext.transactionResult { configuration: Configuration ->
            transform.query(DSL.using(configuration))
        }
    }
}
