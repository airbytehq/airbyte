/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import org.jooq.DSLContext
import java.sql.SQLException

fun interface ContextQueryFunction<T> {
    @Throws(SQLException::class)
    fun query(context: DSLContext?): T
}
