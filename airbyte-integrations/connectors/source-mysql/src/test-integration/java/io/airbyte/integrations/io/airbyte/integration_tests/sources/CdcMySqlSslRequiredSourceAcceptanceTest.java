/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import java.util.stream.Stream;

public class CdcMySqlSslRequiredSourceAcceptanceTest extends CdcMySqlSourceAcceptanceTest {

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withCdcReplication()
        .withSsl(ImmutableMap.builder().put(JdbcUtils.MODE_KEY, "required").build())
        .build();
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) {
    super.setupEnvironment(environment);
    testdb.with("ALTER USER %s REQUIRE SSL;", testdb.getUserName());
  }

  @Override
  protected Stream<String> extraContainerFactoryMethods() {
    return Stream.of("withRootAndServerCertificates", "withClientCertificate");
  }

}
