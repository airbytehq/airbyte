/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import io.airbyte.commons.string.Strings;
import io.airbyte.db.Databases;
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
    createTestData(database, schemaName);
  }

}
