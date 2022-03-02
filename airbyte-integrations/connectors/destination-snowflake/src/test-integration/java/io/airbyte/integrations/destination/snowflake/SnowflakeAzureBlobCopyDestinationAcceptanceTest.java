/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.client.util.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;

public class SnowflakeAzureBlobCopyDestinationAcceptanceTest extends SnowflakeInsertDestinationAcceptanceTest {

  @Override
  public JsonNode getStaticConfig() {
    final JsonNode copyConfig = Jsons.deserialize(IOs.readFile(Path.of("secrets/copy_azure_blob_config.json")));
    Preconditions.checkArgument(SnowflakeDestination.isAzureBlobCopy(copyConfig));
    Preconditions.checkArgument(!SnowflakeDestination.isS3Copy(copyConfig));
    Preconditions.checkArgument(!SnowflakeDestination.isGcsCopy(copyConfig));
    return copyConfig;
  }

}
