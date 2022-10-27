/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

public class DatabricksStagingLocationGetterTest {

  private static final String SECRETS_CONFIG_JSON = "secrets/staging_config.json";

  @Test
  public void testGetStagingLocation() throws IOException, InterruptedException {
    final JsonNode config = Jsons.deserialize(IOs.readFile(Path.of(SECRETS_CONFIG_JSON)));
    final DatabricksStagingLocationGetter stagingLocationGetter = new DatabricksStagingLocationGetter(
        config.get("databricks_username").asText(),
        config.get("databricks_server_hostname").asText(),
        config.get("databricks_personal_access_token").asText());
    final PreSignedUrl preSignedUrl = stagingLocationGetter.getPreSignedUrl(System.currentTimeMillis() + "/test.csv");
    assertTrue(preSignedUrl.url().startsWith("https://"));
    assertTrue(preSignedUrl.expirationTimeMillis() > 0);
  }

}
