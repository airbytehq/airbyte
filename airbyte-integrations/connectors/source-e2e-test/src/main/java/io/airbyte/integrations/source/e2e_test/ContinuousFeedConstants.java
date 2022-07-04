/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import net.jimblackler.jsongenerator.Configuration;
import net.jimblackler.jsongenerator.DefaultConfig;

public final class ContinuousFeedConstants {

  public static final int MOCK_JSON_MAX_TREE_SIZE = 100;
  public static final Configuration MOCK_JSON_CONFIG = DefaultConfig.build()
      .setPedanticTypes(true)
      .setGenerateNulls(false)
      .setGenerateMinimal(false)
      .setGenerateAdditionalProperties(false)
      .setUseRomanCharsOnly(true)
      .setNonRequiredPropertyChance(1.0f)
      .get();

  private ContinuousFeedConstants() {}

}
