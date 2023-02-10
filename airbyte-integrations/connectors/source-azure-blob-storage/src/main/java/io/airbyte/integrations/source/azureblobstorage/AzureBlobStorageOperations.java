package io.airbyte.integrations.source.azureblobstorage;

import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.models.BlobListDetails;
import com.azure.storage.blob.models.ListBlobsOptions;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.saasquatch.jsonschemainferrer.AdditionalPropertiesPolicies;
import com.saasquatch.jsonschemainferrer.JsonSchemaInferrer;
import com.saasquatch.jsonschemainferrer.SpecVersion;
import io.airbyte.commons.functional.CheckedFunction;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;
import org.apache.commons.lang3.StringUtils;

public class AzureBlobStorageOperations {

    private final BlobContainerClient blobContainerClient;

    private final AzureBlobStorageConfig azureBlobStorageConfig;

    private final ObjectMapper objectMapper;

    private final JsonSchemaInferrer jsonSchemaInferrer;

    public AzureBlobStorageOperations(AzureBlobStorageConfig azureBlobStorageConfig) {
        this.objectMapper = new ObjectMapper();
        this.azureBlobStorageConfig = azureBlobStorageConfig;
        this.blobContainerClient = azureBlobStorageConfig.createBlobContainerClient();
        jsonSchemaInferrer = JsonSchemaInferrer.newBuilder()
            .setSpecVersion(SpecVersion.DRAFT_07)
            .setAdditionalPropertiesPolicy(AdditionalPropertiesPolicies.allowed())
            .build();
    }

    public JsonNode inferSchema() {
        var blobs = readBlobs(null);

        // create super schema inferred from all blobs in the container
        var jsonSchema = jsonSchemaInferrer.inferForSamples(blobs);
        ((ObjectNode) jsonSchema.get("properties")).putPOJO(AzureBlobAdditionalProperties.BLOB_NAME,
            Map.of("type", "string"));
        ((ObjectNode) jsonSchema.get("properties")).putPOJO(AzureBlobAdditionalProperties.LAST_MODIFIED,
            Map.of("type", "string"));
        return jsonSchema;

    }

    public List<AzureBlob> listBlobs() {

        var listBlobsOptions = new ListBlobsOptions();
        listBlobsOptions.setDetails(new BlobListDetails()
            .setRetrieveMetadata(true)
            .setRetrieveDeletedBlobs(false));

        if (!StringUtils.isBlank(azureBlobStorageConfig.prefix())) {
            listBlobsOptions.setPrefix(azureBlobStorageConfig.prefix());
        }

        // blobContainerClient.findBlobsByTags()

        // TODO(itaseski) investigate iterable retrieval with continuation token
        var pagedIterable = blobContainerClient.listBlobs(listBlobsOptions, null);

        return pagedIterable.mapPage(blobItem -> new AzureBlob.Builder()
                .withName(blobItem.getName())
                .withLastModified(blobItem.getProperties().getLastModified())
                .build())
            .stream()
            .toList();
    }

    public List<JsonNode> readBlobs(OffsetDateTime offsetDateTime) {
        // TODO (itaseski) add additional fields to blobs
        return listBlobs().stream()
            .filter(ab -> {if (offsetDateTime != null) {return ab.lastModified().isAfter(offsetDateTime);} else {return true;}})
            .map(ab -> blobContainerClient.getBlobClient(ab.name()))
            .map(bc -> handleCheckedIOException(objectMapper::readTree, bc.downloadContent().toStream()))
            .toList();
    }

    private <T, R> R handleCheckedIOException(CheckedFunction<T, R, IOException> checkedFunction, T parameter) {
        try {
            return checkedFunction.apply(parameter);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }


}
