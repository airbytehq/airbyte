package io.airbyte.integrations.source.e2e_test;

import net.jimblackler.jsongenerator.Configuration;

public final class ContinuousFeedConstants {

  public static final int MOCK_JSON_MAX_TREE_SIZE = 100;
  public static final Configuration MOCK_JSON_CONFIG = new Configuration() {
    @Override
    public boolean isPedanticTypes() {
      return true;
    }

    @Override
    public boolean isGenerateNulls() {
      return false;
    }

    @Override
    public boolean isGenerateMinimal() {
      return false;
    }

    @Override
    public float nonRequiredPropertyChance() {
      return 1.0F;
    }
  };

}
