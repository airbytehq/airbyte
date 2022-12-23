/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import java.net.URI;
import software.amazon.awssdk.regions.Region;

public record DynamodbConfig(

                             URI endpoint,

                             Region region,

                             String accessKey,

                             String secretKey

) {

  public static DynamodbConfig createDynamodbConfig(JsonNode jsonNode) {
    JsonNode endpoint = jsonNode.get("endpoint");
    JsonNode region = jsonNode.get("region");
    return new DynamodbConfig(
        endpoint != null && !endpoint.asText().isBlank() ? URI.create(endpoint.asText()) : null,
        region != null && !region.asText().isBlank() ? Region.of(region.asText()) : null,
        jsonNode.get("access_key_id").asText(),
        jsonNode.get("secret_access_key").asText());
  }

}
