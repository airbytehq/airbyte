/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import java.sql.SQLException
import org.jooq.DSLContext

fun interface ContextQueryFunction<T> {
    @Throws(SQLException::class) fun query(context: DSLContext): T
}
