/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveSourceRunner;
import io.airbyte.cdk.integrations.destination.s3.BaseS3Destination;
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfigFactory;
import io.airbyte.cdk.integrations.destination.s3.StorageProvider;
import io.airbyte.cdk.integrations.destination.s3.constant.S3Constants;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.Map;

public class S3Destination extends BaseS3Destination {

  private FeatureFlags featureFlags = new EnvVariableFeatureFlags();

  public void setFeatureFlags(FeatureFlags featureFlags) {
    this.featureFlags = featureFlags;
  }

  public S3Destination() {}

  @VisibleForTesting
  protected S3Destination(final S3DestinationConfigFactory s3DestinationConfigFactory, Map<String, String> env) {
    super(s3DestinationConfigFactory, env);
  }

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new S3Destination()).run(args);
  }

  @Override
  public StorageProvider storageProvider() {
    return StorageProvider.AWS_S3;
  }

  public ConnectorSpecification spec() throws Exception {
    final String resourceString = MoreResources.readResource("spec.json");
    ConnectorSpecification spec = Jsons.deserialize(resourceString, ConnectorSpecification.class);
    if (!AdaptiveSourceRunner.CLOUD_MODE.equalsIgnoreCase(featureFlags.deploymentMode())) {
      ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(S3Constants.ROLE_ARN);
    }
    return spec;
  }

}
