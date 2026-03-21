/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import java.sql.SQLException
import org.jooq.DSLContext

fun interface ContextQueryFunction<T> {
    @Throws(SQLException::class) fun query(context: DSLContext): T
}
