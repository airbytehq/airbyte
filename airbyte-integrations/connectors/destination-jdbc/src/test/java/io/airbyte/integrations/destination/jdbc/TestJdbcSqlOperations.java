/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.List;

public class TestJdbcSqlOperations extends JdbcSqlOperations {

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
                                    final List<AirbyteRecordMessage> records,
                                    final String schemaName,
                                    final String tableName)
      throws Exception {
    // Not required for the testing
  }

}
