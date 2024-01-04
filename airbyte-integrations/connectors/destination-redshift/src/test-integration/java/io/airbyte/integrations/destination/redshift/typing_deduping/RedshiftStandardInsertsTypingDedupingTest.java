/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;

public class RedshiftStandardInsertsTypingDedupingTest extends AbstractRedshiftTypingDedupingTest {

  @Override
  protected JsonNode getBaseConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/1s1t_config.json")));
  }

}
