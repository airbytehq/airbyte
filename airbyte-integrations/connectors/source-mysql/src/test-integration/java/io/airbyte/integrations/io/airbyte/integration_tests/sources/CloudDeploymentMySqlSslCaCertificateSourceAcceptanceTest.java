/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.ContainerModifier;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.apache.commons.lang3.ArrayUtils;

public class CloudDeploymentMySqlSslCaCertificateSourceAcceptanceTest extends MySqlSourceAcceptanceTest {

  private static final String PASSWORD = "Passw0rd";

  @Override
  protected FeatureFlags featureFlags() {
    return FeatureFlagsWrapper.overridingDeploymentMode(super.featureFlags(), "CLOUD");
  }

  @Override
  protected ContainerModifier[] getContainerModifiers() {
    return ArrayUtils.toArray(ContainerModifier.ROOT_AND_SERVER_CERTIFICATES);
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

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return SshHelpers.injectSshIntoSpec(Jsons.deserialize(MoreResources.readResource("expected_cloud_spec.json"), ConnectorSpecification.class));
  }

}
