/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import org.junit.jupiter.api.Disabled;

public class BigQueryStandardInsertsRawOverrideDisableTypingDedupingTest extends AbstractBigQueryTypingDedupingTest {

  @Override
  public String getConfigPath() {
    return "secrets/credentials-1s1t-disabletd-standard-raw-override.json";
  }

  @Override
  protected String getRawDataset() {
    return "overridden_raw_dataset";
  }

  @Override
  protected boolean disableFinalTableComparison() {
    return true;
  }

  @Override
  @Disabled
  public void testRemovingPKNonNullIndexes() throws Exception {
    // Do nothing.
  }

  @Override
  @Disabled
  public void identicalNameSimultaneousSync() throws Exception {
    // TODO: create fixtures to verify how raw tables are affected. Base tests check for final tables.
  }

}
