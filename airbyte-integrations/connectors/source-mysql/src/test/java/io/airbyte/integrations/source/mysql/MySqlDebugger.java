/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mysql;

import io.airbyte.cdk.integrations.debug.DebugUtil;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;

public class MySqlDebugger {

  @SuppressWarnings({"unchecked", "deprecation", "resource"})
  public static void main(final String[] args) throws Exception {
    final MySqlSource mysqlSource = new MySqlSource();
    mysqlSource.setFeatureFlags(FeatureFlagsWrapper.overridingUseStreamCapableState(new EnvVariableFeatureFlags(), true));
    DebugUtil.debug(mysqlSource);
  }

}
