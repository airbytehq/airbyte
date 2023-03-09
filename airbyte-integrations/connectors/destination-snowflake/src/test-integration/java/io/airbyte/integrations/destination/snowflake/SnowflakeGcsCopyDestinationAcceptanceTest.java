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

public class SnowflakeGcsCopyDestinationAcceptanceTest extends SnowflakeInsertDestinationAcceptanceTest {

  private static final String NO_GCS_PRIVILEGES_ERR_MSG =
      "Permission 'storage.objects.create' denied on resource (or it may not exist).";

  @Override
  public JsonNode getStaticConfig() {
    final JsonNode copyConfig = Jsons.deserialize(IOs.readFile(Path.of("secrets/copy_gcs_config.json")));
    Preconditions.checkArgument(SnowflakeDestinationResolver.isGcsCopy(copyConfig));
    Preconditions.checkArgument(!SnowflakeDestinationResolver.isS3Copy(copyConfig));
    return copyConfig;
  }

  @Test
  public void testCheckWithNoProperGcsPermissionConnection() throws Exception {
    // Config to user (creds) that has no permission to schema
    final JsonNode config = Jsons.deserialize(IOs.readFile(
        Path.of("secrets/copy_insufficient_gcs_roles_config.json")));

    StandardCheckConnectionOutput standardCheckConnectionOutput = runCheck(config);

    assertEquals(Status.FAILED, standardCheckConnectionOutput.getStatus());
    assertThat(standardCheckConnectionOutput.getMessage()).contains(NO_GCS_PRIVILEGES_ERR_MSG);
  }

}
