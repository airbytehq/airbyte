/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

import io.airbyte.commons.functional.CheckedBiConsumer
import java.sql.*

/*
 * Interface that defines how to stream results from a Jdbc database. This involves determining
 * updating what the fetch size should be based on the size of the existing rows. 1. The config
 * initializes the fetch size and sets up the estimator. 2. The config then accepts each row and
 * feeds it to the estimator. If the estimator has a new estimate, it updates the fetch size.
 */
interface JdbcStreamingQueryConfig : CheckedBiConsumer<ResultSet, Any, SQLException> {
    @Throws(SQLException::class) fun initialize(connection: Connection, statement: Statement)
}
