/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azureblobstorage.format;

import com.azure.storage.blob.BlobClient;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.saasquatch.jsonschemainferrer.AdditionalPropertiesPolicies;
import com.saasquatch.jsonschemainferrer.JsonSchemaInferrer;
import com.saasquatch.jsonschemainferrer.SpecVersion;
import io.airbyte.integrations.source.azureblobstorage.AzureBlob;
import io.airbyte.integrations.source.azureblobstorage.AzureBlobAdditionalProperties;
import io.airbyte.integrations.source.azureblobstorage.AzureBlobStorageConfig;
import io.airbyte.integrations.source.azureblobstorage.AzureBlobStorageOperations;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.UncheckedIOException;
import java.nio.charset.Charset;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;

public class JsonlAzureBlobStorageOperations extends AzureBlobStorageOperations {

  private final ObjectMapper objectMapper;

  private final JsonSchemaInferrer jsonSchemaInferrer;

  public JsonlAzureBlobStorageOperations(AzureBlobStorageConfig azureBlobStorageConfig) {
    super(azureBlobStorageConfig);
    this.objectMapper = new ObjectMapper();
    this.jsonSchemaInferrer = JsonSchemaInferrer.newBuilder()
        .setSpecVersion(SpecVersion.DRAFT_07)
        .setAdditionalPropertiesPolicy(AdditionalPropertiesPolicies.allowed())
        .build();
  }

  @Override
  public JsonNode inferSchema() {
    var blobs = readBlobs(null, azureBlobStorageConfig.schemaInferenceLimit());

    // create super schema inferred from all blobs in the container
    var jsonSchema = jsonSchemaInferrer.inferForSamples(blobs);

    if (!jsonSchema.has("properties")) {
      jsonSchema.putObject("properties");
    }

    ((ObjectNode) jsonSchema.get("properties")).putPOJO(AzureBlobAdditionalProperties.BLOB_NAME,
        Map.of("type", "string"));
    ((ObjectNode) jsonSchema.get("properties")).putPOJO(AzureBlobAdditionalProperties.LAST_MODIFIED,
        Map.of("type", "string"));
    return jsonSchema;
  }

  @Override
  public List<JsonNode> readBlobs(OffsetDateTime offsetDateTime) {
    return readBlobs(offsetDateTime, null);
  }

  private List<JsonNode> readBlobs(OffsetDateTime offsetDateTime, Long limit) {
    record DecoratedAzureBlob(AzureBlob azureBlob, BlobClient blobClient) {}

    var blobsStream = limit == null ? listBlobs().stream() : listBlobs().stream().limit(limit);

    return blobsStream
        .filter(ab -> {
          if (offsetDateTime != null) {
            return ab.lastModified().isAfter(offsetDateTime);
          } else {
            return true;
          }
        })
        .map(ab -> new DecoratedAzureBlob(ab, blobContainerClient.getBlobClient(ab.name())))
        .map(dab -> {
          try (
              var br = new BufferedReader(
                  new InputStreamReader(dab.blobClient().downloadContent().toStream(), Charset.defaultCharset()))) {
            return br.lines().map(line -> {
              var jsonNode =
                  handleCheckedIOException(objectMapper::readTree, line);
              ((ObjectNode) jsonNode).put(AzureBlobAdditionalProperties.BLOB_NAME, dab.azureBlob().name());
              ((ObjectNode) jsonNode).put(AzureBlobAdditionalProperties.LAST_MODIFIED,
                  dab.azureBlob().lastModified().toString());
              return jsonNode;
            })
                // need to materialize stream otherwise reader gets closed on return
                .toList();
          } catch (IOException e) {
            throw new UncheckedIOException(e);
          }
        })
        .flatMap(List::stream)
        .toList();
  }

}
