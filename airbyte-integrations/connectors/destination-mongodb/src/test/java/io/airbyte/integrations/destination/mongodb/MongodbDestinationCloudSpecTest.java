/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveSourceRunner;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.Map;
import org.junit.jupiter.api.Test;

public class MongodbDestinationCloudSpecTest {

  private static MongodbDestination cloudDestination() {
    return new MongodbDestination(
        FeatureFlagsWrapper.overridingDeploymentMode(new EnvVariableFeatureFlags(), AdaptiveSourceRunner.CLOUD_MODE));
  }

  private static boolean standaloneInstanceHasTlsProperty(final ConnectorSpecification spec) {
    return spec.getConnectionSpecification()
        .get("properties")
        .get("instance_type")
        .get("oneOf")
        .get(0)
        .get("properties")
        .has("tls");
  }

  private static JsonNode standaloneConfigWithTlsDisabled() {
    return Jsons.jsonNode(Map.of(
        "instance_type", Jsons.jsonNode(Map.of(
            "instance", "standalone",
            JdbcUtils.HOST_KEY, "localhost",
            JdbcUtils.PORT_KEY, 27017,
            "tls", false)),
        JdbcUtils.DATABASE_KEY, "db"));
  }

  @Test
  void testCloudSpecMatchesExpected() throws Exception {
    final ConnectorSpecification expected =
        Jsons.deserialize(MoreResources.readResource("expected_cloud_spec.json"), ConnectorSpecification.class);
    final Destination destination =
        new SshWrappedDestination(cloudDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
    assertEquals(expected, destination.spec());
  }

  @Test
  void testCloudSpecOmitsStandaloneTlsProperty() throws Exception {
    assertFalse(standaloneInstanceHasTlsProperty(cloudDestination().spec()));
  }

  @Test
  void testOssSpecKeepsStandaloneTlsProperty() throws Exception {
    assertTrue(standaloneInstanceHasTlsProperty(new MongodbDestination().spec()));
  }

  @Test
  void testCloudCheckRejectsStandaloneWithTlsDisabled() {
    assertThrows(ConfigErrorException.class, () -> cloudDestination().check(standaloneConfigWithTlsDisabled()));
  }

  @Test
  void testCloudCheckIgnoresTopLevelTlsOverride() {
    // the standalone connection string only honors instance_type.tls, so a top-level tls=true must not
    // satisfy the cloud requirement
    final JsonNode config = ((ObjectNode) standaloneConfigWithTlsDisabled()).put(JdbcUtils.TLS_KEY, true);
    assertThrows(ConfigErrorException.class, () -> cloudDestination().check(config));
  }

  @Test
  void testCloudCheckRejectsLegacyConfig() {
    // legacy host/port configs (no instance_type) always build a connection string with ssl=false
    final JsonNode legacyConfig = Jsons.jsonNode(Map.of(
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, 27017,
        JdbcUtils.DATABASE_KEY, "db"));
    assertThrows(ConfigErrorException.class, () -> cloudDestination().check(legacyConfig));
  }

  @Test
  void testOssCheckAllowsStandaloneWithoutTls() {
    assertDoesNotThrow(() -> new MongodbDestination().enforceCloudTls(standaloneConfigWithTlsDisabled()));
  }

}
