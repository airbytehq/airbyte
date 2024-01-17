/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public class RedshiftStandardInsertsRawSchemaOverrideDisableTypingDedupingTest extends AbstractRedshiftTypingDedupingTest {

  @Override
  protected String getConfigPath() {
    return "secrets/1s1t_config_raw_schema_override.json";
  }

  @Override
  protected String getRawSchema() {
    return "overridden_raw_dataset";
  }

  @Override
  protected boolean disableFinalTableComparison() {
    return true;
  }

  @Disabled
  @Test
  @Override
  public void identicalNameSimultaneousSync() {}

}
