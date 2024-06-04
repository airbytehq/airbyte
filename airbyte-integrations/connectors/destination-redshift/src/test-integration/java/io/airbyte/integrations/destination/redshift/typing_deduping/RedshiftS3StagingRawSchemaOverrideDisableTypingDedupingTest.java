/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public class RedshiftS3StagingRawSchemaOverrideDisableTypingDedupingTest extends AbstractRedshiftTypingDedupingTest {

  @Override
  protected ObjectNode getBaseConfig() {
    return (ObjectNode) Jsons.deserialize(IOs.readFile(Path.of("secrets/1s1t_config_staging_raw_schema_override.json")));
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
