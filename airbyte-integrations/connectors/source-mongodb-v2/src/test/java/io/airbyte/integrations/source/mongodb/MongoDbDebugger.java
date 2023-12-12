/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mongodb;

import io.airbyte.cdk.integrations.debug.DebugUtil;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;

public class MongoDbDebugger {

  @SuppressWarnings({"unchecked", "deprecation", "resource"})
  public static void main(final String[] args) throws Exception {
    final MongoDbSource mongoDbSource = new MongoDbSource();
    mongoDbSource.setFeatureFlags(FeatureFlagsWrapper.overridingUseStreamCapableState(new EnvVariableFeatureFlags(), true));
    DebugUtil.debug(mongoDbSource);
  }
}