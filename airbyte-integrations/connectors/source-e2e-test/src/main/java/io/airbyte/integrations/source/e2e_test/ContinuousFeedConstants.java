/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import net.jimblackler.jsongenerator.Configuration;
import net.jimblackler.jsongenerator.DefaultConfig;

public final class ContinuousFeedConstants {

  public static final int MOCK_JSON_MAX_TREE_SIZE = 100;
  public static final Configuration MOCK_JSON_CONFIG = new DefaultConfig();

  private ContinuousFeedConstants() {}

}
