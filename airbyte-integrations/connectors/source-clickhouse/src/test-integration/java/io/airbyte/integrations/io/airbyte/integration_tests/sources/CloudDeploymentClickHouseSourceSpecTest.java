/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveSourceRunner;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedSource;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.clickhouse.ClickHouseSource;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.junit.jupiter.api.Test;

public class CloudDeploymentClickHouseSourceSpecTest {

  private Source cloudSource() {
    final ClickHouseSource source = new ClickHouseSource(
        FeatureFlagsWrapper.overridingDeploymentMode(
            new EnvVariableFeatureFlags(), AdaptiveSourceRunner.CLOUD_MODE));
    return new SshWrappedSource(source, JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  @Test
  void testCloudDeploymentSpecRemovesSslProperty() throws Exception {
    final ConnectorSpecification actual = cloudSource().spec();

    final ConnectorSpecification expected =
        SshHelpers.injectSshIntoSpec(
            Jsons.deserialize(MoreResources.readResource("expected_cloud_spec.json"), ConnectorSpecification.class));

    assertEquals(expected, actual);
  }

  @Test
  void testCloudDeploymentSpecDoesNotContainSslProperty() throws Exception {
    final ConnectorSpecification spec = cloudSource().spec();

    assertFalse(spec.getConnectionSpecification().get("properties").has("ssl"),
        "Cloud deployment spec should not contain the 'ssl' property");
  }

  @Test
  void testOssDeploymentSpecContainsSslProperty() throws Exception {
    final Source source = ClickHouseSource.getWrappedSource();

    final ConnectorSpecification spec = source.spec();

    assertTrue(spec.getConnectionSpecification().get("properties").has("ssl"),
        "OSS deployment spec should contain the 'ssl' property");
  }

}
