/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

import java.sql.*

class NoOpStreamingQueryConfig : JdbcStreamingQueryConfig {
    @Throws(SQLException::class)
    override fun initialize(connection: Connection, statement: Statement) {}

    @Throws(SQLException::class) override fun accept(resultSet: ResultSet, o: Any) {}
}
