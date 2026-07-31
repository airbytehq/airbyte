/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveSourceRunner;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.Map;
import org.junit.jupiter.api.Test;

class OracleDestinationCloudSpecTest {

  private static OracleDestination cloudDestination() {
    return new OracleDestination(
        FeatureFlagsWrapper.overridingDeploymentMode(new EnvVariableFeatureFlags(), AdaptiveSourceRunner.CLOUD_MODE));
  }

  private static JsonNode unencryptedConfig() {
    return Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, 1521,
        JdbcUtils.USERNAME_KEY, "user",
        "sid", "db",
        JdbcUtils.ENCRYPTION_KEY, Jsons.jsonNode(Map.of(OracleDestination.ENCRYPTION_METHOD_KEY, "unencrypted"))));
  }

  @Test
  void testCloudSpecMatchesExpected() throws Exception {
    final ConnectorSpecification expected = SshHelpers.injectSshIntoSpec(
        Jsons.deserialize(MoreResources.readResource("expected_cloud_spec.json"), ConnectorSpecification.class));
    final Destination destination =
        new SshWrappedDestination(cloudDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
    assertEquals(expected, destination.spec());
  }

  @Test
  void testCloudSpecOmitsEncryptionOption() throws Exception {
    assertFalse(cloudDestination().spec().getConnectionSpecification().get("properties").has(JdbcUtils.ENCRYPTION_KEY));
  }

  @Test
  void testOssSpecKeepsEncryptionOption() throws Exception {
    assertTrue(new OracleDestination().spec().getConnectionSpecification().get("properties").has(JdbcUtils.ENCRYPTION_KEY));
  }

  @Test
  void testCloudModeForcesNativeNetworkEncryption() {
    final JsonNode enforcedConfig = cloudDestination().withEnforcedEncryption(unencryptedConfig());
    final JsonNode encryption = enforcedConfig.get(JdbcUtils.ENCRYPTION_KEY);
    assertEquals("client_nne", encryption.get(OracleDestination.ENCRYPTION_METHOD_KEY).asText());
    assertEquals("AES256", encryption.get("encryption_algorithm").asText());

    final Map<String, String> properties = cloudDestination().getDefaultConnectionProperties(unencryptedConfig());
    assertEquals("REQUIRED", properties.get("oracle.net.encryption_client"));
    assertEquals("( AES256 )", properties.get("oracle.net.encryption_types_client"));
  }

  @Test
  void testOssModeHonorsUnencryptedConfig() {
    assertTrue(new OracleDestination().getDefaultConnectionProperties(unencryptedConfig()).isEmpty());
  }

}
