/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import io.airbyte.commons.string.Strings;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.redshift.RedshiftSource;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;

public class RedshiftSslSourceAcceptanceTest extends RedshiftSourceAcceptanceTest {

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    config = getStaticConfig();

    database = Databases.createJdbcDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:redshift://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        RedshiftSource.DRIVER_CLASS,
        "ssl=true;" +
            "sslfactory=com.amazon.redshift.ssl.NonValidatingFactory");

    schemaName = Strings.addRandomSuffix("integration_test", "_", 5).toLowerCase();
    final String createSchemaQuery = String.format("CREATE SCHEMA %s", schemaName);
    database.execute(connection -> {
      connection.createStatement().execute(createSchemaQuery);
    });

    streamName = "customer";
    final String fqTableName = JdbcUtils.getFullyQualifiedTableName(schemaName, streamName);
    final String createTestTable =
        String.format("CREATE TABLE IF NOT EXISTS %s (c_custkey INTEGER, c_name VARCHAR(16), c_nation VARCHAR(16));\n", fqTableName);
    database.execute(connection -> {
      connection.createStatement().execute(createTestTable);
    });

    final String insertTestData = String.format("insert into %s values (1, 'Chris', 'France');\n", fqTableName);
    database.execute(connection -> {
      connection.createStatement().execute(insertTestData);
    });
  }

}
