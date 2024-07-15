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

                             List<String> reservedAttributeNames,

                             boolean ignoreMissingPermissions

) {

  public static DynamodbConfig createDynamodbConfig(JsonNode jsonNode) {
    JsonNode credentials = jsonNode.get("credentials");
    JsonNode accessKeyId = credentials.get("access_key_id");
    JsonNode secretAccessKey = credentials.get("secret_access_key");

    JsonNode endpoint = jsonNode.get("endpoint");
    JsonNode region = jsonNode.get("region");
    JsonNode attributeNames = jsonNode.get("reserved_attribute_names");
    JsonNode missingPermissions = jsonNode.get("ignore_missing_read_permissions_tables");
    return new DynamodbConfig(
        endpoint != null && !endpoint.asText().isBlank() ? URI.create(endpoint.asText()) : null,
        region != null && !region.asText().isBlank() ? Region.of(region.asText()) : null,
        accessKeyId != null && !accessKeyId.asText().isBlank() ? accessKeyId.asText() : null,
        secretAccessKey != null && !secretAccessKey.asText().isBlank() ? secretAccessKey.asText() : null,
        attributeNames != null ? Arrays.asList(attributeNames.asText().split("\\s*,\\s*")) : List.of(),
        missingPermissions != null ? missingPermissions.asBoolean() : false);
  }

}
