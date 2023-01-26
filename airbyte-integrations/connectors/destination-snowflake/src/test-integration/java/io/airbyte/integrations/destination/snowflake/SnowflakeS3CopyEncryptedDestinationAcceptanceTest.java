/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

public class SnowflakeS3CopyEncryptedDestinationAcceptanceTest extends SnowflakeInsertDestinationAcceptanceTest {

  private static final String NO_S3_PRIVILEGES_ERR_MSG = "Could not connect with provided configuration.";

  @Override
  public JsonNode getStaticConfig() {
    final JsonNode copyConfig = Jsons.deserialize(IOs.readFile(Path.of("secrets/copy_s3_encrypted_config.json")));
    Preconditions.checkArgument(SnowflakeDestinationResolver.isS3Copy(copyConfig));
    Preconditions.checkArgument(!SnowflakeDestinationResolver.isGcsCopy(copyConfig));
    return copyConfig;
  }

  @Test
  public void testCheckWithNoProperS3PermissionConnection() throws Exception {
    // Config to user (creds) that has no permission to schema
    final JsonNode config = Jsons.deserialize(IOs.readFile(
        Path.of("secrets/copy_s3_wrong_location_config.json")));

    StandardCheckConnectionOutput standardCheckConnectionOutput = runCheck(config);

    assertEquals(Status.FAILED, standardCheckConnectionOutput.getStatus());
    assertThat(standardCheckConnectionOutput.getMessage()).contains(NO_S3_PRIVILEGES_ERR_MSG);
  }

}
