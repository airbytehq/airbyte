/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveSourceRunner;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.Map;
import org.junit.jupiter.api.Test;

public class ElasticsearchDestinationCloudSpecTest {

  private static ElasticsearchDestination cloudDestination() {
    return new ElasticsearchDestination(
        FeatureFlagsWrapper.overridingDeploymentMode(new EnvVariableFeatureFlags(), AdaptiveSourceRunner.CLOUD_MODE));
  }

  private static boolean hasNoneAuthOption(final ConnectorSpecification spec) {
    for (final JsonNode option : spec.getConnectionSpecification().get("properties").get("authenticationMethod").get("oneOf")) {
      if ("None".equals(option.get("title").asText())) {
        return true;
      }
    }
    return false;
  }

  @Test
  void testCloudSpecMatchesExpected() throws Exception {
    final ConnectorSpecification expected =
        Jsons.deserialize(MoreResources.readResource("expected_cloud_spec.json"), ConnectorSpecification.class);
    assertEquals(expected, cloudDestination().spec());
  }

  @Test
  void testCloudSpecOmitsNoneAuthOption() throws Exception {
    assertFalse(hasNoneAuthOption(cloudDestination().spec()));
  }

  @Test
  void testOssSpecKeepsNoneAuthOption() throws Exception {
    assertTrue(hasNoneAuthOption(new ElasticsearchDestination().spec()));
  }

  @Test
  void testCloudCheckRejectsHttpEndpoint() throws Exception {
    final JsonNode config = Jsons.jsonNode(Map.of("endpoint", "http://localhost:9200"));
    final AirbyteConnectionStatus status = cloudDestination().check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertEquals("Server Endpoint requires HTTPS", status.getMessage());
  }

}
