/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.ContainerModifier;
import org.apache.commons.lang3.ArrayUtils;

public class MySqlSslFullCertificateSourceAcceptanceTest extends MySqlSourceAcceptanceTest {

  private static final String PASSWORD = "Passw0rd";

  @Override
  protected ContainerModifier[] getContainerModifiers() {
    return ArrayUtils.toArray(ContainerModifier.ROOT_AND_SERVER_CERTIFICATES, ContainerModifier.CLIENT_CERTITICATE);
  }

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withStandardReplication()
        .withSsl(ImmutableMap.builder()
            .put(JdbcUtils.MODE_KEY, "verify_ca")
            .put("ca_certificate", testdb.getCertificates().caCertificate())
            .put("client_certificate", testdb.getCertificates().clientCertificate())
            .put("client_key", testdb.getCertificates().clientKey())
            .put("client_key_password", PASSWORD)
            .build())
        .build();
  }

}
