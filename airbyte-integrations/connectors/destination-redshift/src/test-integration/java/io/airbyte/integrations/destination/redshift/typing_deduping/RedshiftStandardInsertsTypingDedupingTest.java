/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

public class RedshiftStandardInsertsTypingDedupingTest extends AbstractRedshiftTypingDedupingTest {

  @Override
  protected String getConfigPath() {
    return "secrets/1s1t_config.json";
  }

}
