/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import java.nio.file.Path;
import java.util.Optional;

public class SnowflakeInternalStagingDestinationAcceptanceTest extends SnowflakeInsertDestinationAcceptanceTest {

  private static final NamingConventionTransformer NAME_TRANSFORMER = new SnowflakeSQLNameTransformer();

  public JsonNode getStaticConfig() {
    final JsonNode internalStagingConfig = Jsons.deserialize(IOs.readFile(Path.of("secrets/internal_staging_config.json")));
    Preconditions.checkArgument(!SnowflakeDestinationResolver.isS3Copy(internalStagingConfig));
    Preconditions.checkArgument(!SnowflakeDestinationResolver.isGcsCopy(internalStagingConfig));
    return internalStagingConfig;
  }

  @Override
  protected boolean supportNamespaceTest() {
    return true;
  }

  @Override
  protected Optional<NamingConventionTransformer> getNameTransformer() {
    return Optional.of(NAME_TRANSFORMER);
  }

}
