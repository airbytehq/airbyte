/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.acceptance;

import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.test.acceptance.AcceptanceTests.Type;
import java.util.HashMap;
import java.util.Map;
import org.jooq.SQLDialect;

/**
 * This class is used to provide information related to the test databases for running the
 * {@link AcceptanceTests} on GKE. We launch 2 postgres databases in GKE as pods which act as source
 * and destination and the tests run against them. In order to allow the test instance to connect to
 * these databases we use port forwarding Refer
 * tools/bin/gke-kube-acceptance-test/acceptance_test_kube_gke.sh for more info
 */
public class GKEPostgresConfig {

  private static final String SOURCE_HOST = "postgres-source-svc";
  private static final String DESTINATION_HOST = "postgres-destination-svc";
  private static final Integer PORT = 5432;
  private static final String USERNAME = "postgresadmin";
  private static final String PASSWORD = "admin123";
  private static final String DB = "postgresdb";

  public static Map<Object, Object> dbConfig(final Type connectorType, final boolean hiddenPassword, final boolean withSchema) {
    final Map<Object, Object> dbConfig = new HashMap<>();
    dbConfig.put("host", connectorType == Type.SOURCE ? SOURCE_HOST : DESTINATION_HOST);
    dbConfig.put("password", hiddenPassword ? "**********" : PASSWORD);

    dbConfig.put("port", PORT);
    dbConfig.put("database", DB);
    dbConfig.put("username", USERNAME);

    if (withSchema) {
      dbConfig.put("schema", "public");
    }

    return dbConfig;
  }

  public static Database getSourceDatabase() {
    return new Database(DSLContextFactory.create(USERNAME, PASSWORD, DatabaseDriver.POSTGRESQL.getDriverClassName(),
        "jdbc:postgresql://localhost:2000/postgresdb", SQLDialect.POSTGRES));
  }

  public static Database getDestinationDatabase() {
    return new Database(DSLContextFactory.create(USERNAME, PASSWORD, DatabaseDriver.POSTGRESQL.getDriverClassName(),
        "jdbc:postgresql://localhost:3000/postgresdb", SQLDialect.POSTGRES));
  }

}
