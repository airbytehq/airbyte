/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import com.fasterxml.jackson.databind.JsonNode
import java.util.stream.Stream

abstract class SqlDatabase : AbstractDatabase() {
    @Throws(Exception::class) abstract fun execute(sql: String?)

    @Throws(Exception::class)
    abstract fun unsafeQuery(sql: String?, vararg params: String): Stream<JsonNode>
}
