/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yugabytedb;

import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import java.util.Collections;
import javax.sql.DataSource;

public class YugabyteDataSource {

  private YugabyteDataSource() {

  }

  static DataSource getInstance(String host, int port, String database, String username, String password) {
    String jdbcUrl = "jdbc:yugabytedb://" + host + ":" + port + "/" + database;
    return DataSourceFactory.create(
        username,
        password,
        DatabaseDriver.YUGABYTEDB.getDriverClassName(),
        jdbcUrl,
        Collections.emptyMap());
  }

}
