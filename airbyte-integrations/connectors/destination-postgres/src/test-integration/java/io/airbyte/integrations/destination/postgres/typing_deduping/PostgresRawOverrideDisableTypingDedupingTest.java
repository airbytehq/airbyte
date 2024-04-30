/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping;

import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public class PostgresRawOverrideDisableTypingDedupingTest extends PostgresTypingDedupingTest {

  @Override
  protected ObjectNode getBaseConfig() {
    return super.getBaseConfig()
        .put("raw_data_schema", "overridden_raw_dataset")
        .put("disable_type_dedupe", true);
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

  @Disabled
  @Test
  @Override
  public void testVarcharLimitOver64K() {}

}
