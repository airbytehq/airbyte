/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;

/**
 * Integration test testing the {@link RedshiftInsertDestination}. As the Redshift test credentials
 * contain S3 credentials by default, we remove these credentials.
 */
public class RedshiftInsertDestinationAcceptanceTest extends RedshiftCopyDestinationAcceptanceTest {

  public JsonNode getStaticConfig() {
    return purge(Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json"))));
  }

  public static JsonNode purge(JsonNode config) {
    var original = (ObjectNode) Jsons.clone(config);
    original.remove("s3_bucket_name");
    original.remove("s3_bucket_region");
    original.remove("access_key_id");
    original.remove("secret_access_key");
    return original;
  }

}
