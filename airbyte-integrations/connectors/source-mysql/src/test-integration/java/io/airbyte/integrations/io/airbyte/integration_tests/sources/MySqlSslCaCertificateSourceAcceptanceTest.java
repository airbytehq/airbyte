/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import java.util.stream.Stream;

public class MySqlSslCaCertificateSourceAcceptanceTest extends MySqlSourceAcceptanceTest {

  private static final String PASSWORD = "Passw0rd";

  @Override
  protected Stream<String> extraContainerFactoryMethods() {
    return Stream.of("withRootAndServerCertificates");
  }

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withStandardReplication()
        .withSsl(ImmutableMap.builder()
            .put(JdbcUtils.MODE_KEY, "verify_ca")
            .put("ca_certificate", testdb.getCaCertificate())
            .put("client_key_password", PASSWORD)
            .build())
        .build();
  }

}
