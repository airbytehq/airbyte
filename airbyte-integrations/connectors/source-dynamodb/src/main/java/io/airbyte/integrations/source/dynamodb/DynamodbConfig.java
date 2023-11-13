/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import java.net.URI;
import java.util.Arrays;
import java.util.List;
import software.amazon.awssdk.regions.Region;

public record DynamodbConfig(

                             URI endpoint,

                             Region region,

                             String accessKey,

                             String secretKey,

                             List<String> reservedAttributeNames

) {

  public static DynamodbConfig createDynamodbConfig(JsonNode jsonNode) {
    JsonNode endpoint = jsonNode.get("endpoint");
    JsonNode region = jsonNode.get("region");
    JsonNode attributeNames = jsonNode.get("reserved_attribute_names");
    return new DynamodbConfig(
        endpoint != null && !endpoint.asText().isBlank() ? URI.create(endpoint.asText()) : null,
        region != null && !region.asText().isBlank() ? Region.of(region.asText()) : null,
        jsonNode.get("access_key_id").asText(),
        jsonNode.get("secret_access_key").asText(),
        attributeNames != null ? Arrays.asList(attributeNames.asText().split("\\s*,\\s*")) : List.of());
  }

}
