/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
    Preconditions.checkArgument(SnowflakeDestinationResolver.isAzureBlobCopy(copyConfig));
    Preconditions.checkArgument(!SnowflakeDestinationResolver.isS3Copy(copyConfig));
    Preconditions.checkArgument(!SnowflakeDestinationResolver.isGcsCopy(copyConfig));
    return copyConfig;
  }

}
