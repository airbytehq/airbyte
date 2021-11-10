/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import io.airbyte.commons.functional.CheckedBiConsumer;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public interface JdbcStreamingQueryConfiguration extends CheckedBiConsumer<Connection, PreparedStatement, SQLException> {

}
