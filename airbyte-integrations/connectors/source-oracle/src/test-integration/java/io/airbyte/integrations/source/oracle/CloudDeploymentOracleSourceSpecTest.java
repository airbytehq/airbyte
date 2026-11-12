/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveSourceRunner;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedSource;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.junit.jupiter.api.Test;

public class CloudDeploymentOracleSourceSpecTest {

  @Test
  void testCloudDeploymentSpecMatchesExpected() throws Exception {
    final OracleSource oracleSource = new OracleSource(
        FeatureFlagsWrapper.overridingDeploymentMode(new EnvVariableFeatureFlags(), AdaptiveSourceRunner.CLOUD_MODE));
    final Source source = new SshWrappedSource(oracleSource, JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
    final ConnectorSpecification actual = source.spec();
    final ConnectorSpecification expected =
        Jsons.deserialize(MoreResources.readResource("expected_cloud_spec.json"), ConnectorSpecification.class);
    assertEquals(expected, actual);
  }

  @Test
  void testCloudDeploymentSpecDoesNotContainUnencryptedOption() throws Exception {
    final OracleSource oracleSource = new OracleSource(
        FeatureFlagsWrapper.overridingDeploymentMode(new EnvVariableFeatureFlags(), AdaptiveSourceRunner.CLOUD_MODE));
    final Source source = new SshWrappedSource(oracleSource, JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
    final ConnectorSpecification spec = source.spec();
    final JsonNode encryptionOneOf = spec.getConnectionSpecification().get("properties").get("encryption").get("oneOf");
    for (final JsonNode option : encryptionOneOf) {
      assertFalse("unencrypted".equals(
          option.path("properties").path("encryption_method").path("const").asText()),
          "Cloud spec should not contain the 'unencrypted' encryption option");
    }
    // encryption should be required
    final JsonNode required = spec.getConnectionSpecification().get("required");
    boolean encryptionRequired = false;
    for (final JsonNode r : required) {
      if ("encryption".equals(r.asText())) {
        encryptionRequired = true;
      }
    }
    assertTrue(encryptionRequired, "Cloud spec should require 'encryption'");
  }

  @Test
  void testOssDeploymentSpecContainsUnencryptedOption() throws Exception {
    final OracleSource oracleSource = new OracleSource();
    final Source source = new SshWrappedSource(oracleSource, JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
    final ConnectorSpecification spec = source.spec();
    final JsonNode encryptionOneOf = spec.getConnectionSpecification().get("properties").get("encryption").get("oneOf");
    boolean hasUnencrypted = false;
    for (final JsonNode option : encryptionOneOf) {
      if ("unencrypted".equals(
          option.path("properties").path("encryption_method").path("const").asText())) {
        hasUnencrypted = true;
      }
    }
    assertTrue(hasUnencrypted, "OSS spec should contain the 'unencrypted' encryption option");
    // encryption should NOT be required in OSS mode
    final JsonNode required = spec.getConnectionSpecification().get("required");
    boolean encryptionRequired = false;
    for (final JsonNode r : required) {
      if ("encryption".equals(r.asText())) {
        encryptionRequired = true;
      }
    }
    assertFalse(encryptionRequired, "OSS spec should not require 'encryption'");
  }

}
