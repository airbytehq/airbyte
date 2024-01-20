/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping;

import com.fasterxml.jackson.databind.node.ObjectNode;

public class PostgresRawOverrideTypingDedupingTest extends PostgresTypingDedupingTest {

  @Override
  protected ObjectNode getBaseConfig() {
    return super.getBaseConfig()
        .put("raw_data_schema", "overridden_raw_dataset");
  }

  @Override
  protected String getRawSchema() {
    return "overridden_raw_dataset";
  }

}
