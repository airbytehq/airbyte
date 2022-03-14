/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;

public class SnowflakeInternalStagingDestinationAcceptanceTest extends SnowflakeInsertDestinationAcceptanceTest {

  public JsonNode getStaticConfig() {
    final JsonNode internalStagingConfig = Jsons.deserialize(IOs.readFile(Path.of("secrets/internal_staging_config.json")));
    Preconditions.checkArgument(!SnowflakeDestinationResolver.isS3Copy(internalStagingConfig));
    Preconditions.checkArgument(!SnowflakeDestinationResolver.isGcsCopy(internalStagingConfig));
    return internalStagingConfig;
  }

}
