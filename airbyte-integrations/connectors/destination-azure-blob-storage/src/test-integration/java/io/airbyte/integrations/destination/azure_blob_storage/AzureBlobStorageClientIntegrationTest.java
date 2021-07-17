package io.airbyte.integrations.destination.azure_blob_storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.azure.core.http.rest.PagedIterable;
import com.azure.storage.blob.models.BlobItem;
import com.azure.storage.blob.specialized.BlobOutputStream;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class AzureBlobStorageClientIntegrationTest {

  protected final String secretFilePath = "secrets/config.json";
  // TODO fix file path!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  protected final String loremIpsumShortFilePath = "/home/ievgeniit/Code/airbyte/airbyte-integrations/connectors/destination-azure-blob-storage/src/main/resources/LoremIpsumShort.txt";
  private AzureBlobStorageDestinationConfig azureBlobStorageConfig;

  @BeforeEach
  public void beforeAll() {
    JsonNode config = Jsons.deserialize(IOs.readFile(Path.of(secretFilePath)));
    azureBlobStorageConfig = AzureBlobStorageDestinationConfig
        .getAzureBlobStorageConfig(config);
  }


  @Test
  public void testSingleRun() {
    AzureBlobStorageClient c = new AzureBlobStorageClient(azureBlobStorageConfig, false);
    c.writeUsingAppendBlock("Some test text to write");

    PagedIterable<BlobItem> blobItems = c.listBlobsInContainer();
    Optional<BlobItem> first = blobItems.stream()
        .filter(blobItem -> blobItem.getName().equals(azureBlobStorageConfig.getBlobName()))
        .findFirst();

    c.deleteBlob();

    assertTrue(first.isPresent());
    assertEquals(azureBlobStorageConfig.getBlobName(), first.get().getName());
  }


  @Test
  public void testUploadFromFileRun() throws IOException {

    AzureBlobStorageDestinationConfig aconfig1 = new AzureBlobStorageDestinationConfig(
        azureBlobStorageConfig.getEndpointUrl(),
        azureBlobStorageConfig.getAccountName(),
        azureBlobStorageConfig.getAccountKey(),
        "containernameforthread",
        "blobname1file" + System.currentTimeMillis());

    AzureBlobStorageClient c1 = new AzureBlobStorageClient(aconfig1, false);

    byte[] bytes = Files.readAllBytes(Paths.get(loremIpsumShortFilePath));

    BlobOutputStream blobOutputStream = c1.getBlobOutputStream();
    blobOutputStream.write(bytes);
    blobOutputStream.close();

    // TODO enable when finish testing
    c1.deleteBlob();

  }

  @Test
  public void test2simultaneousRun() throws IOException {

    AzureBlobStorageDestinationConfig aconfig1 = new AzureBlobStorageDestinationConfig(
        azureBlobStorageConfig.getEndpointUrl(),
        azureBlobStorageConfig.getAccountName(),
        azureBlobStorageConfig.getAccountKey(),
        "containernameforthread",
        "blobname1" + System.currentTimeMillis());

    AzureBlobStorageClient c1 = new AzureBlobStorageClient(aconfig1, false);

    AzureBlobStorageDestinationConfig aconfig2 = new AzureBlobStorageDestinationConfig(
        azureBlobStorageConfig.getEndpointUrl(),
        azureBlobStorageConfig.getAccountName(),
        azureBlobStorageConfig.getAccountKey(),
        "containernameforthread",
        "blobname1" + System.currentTimeMillis());

    AzureBlobStorageClient c2 = new AzureBlobStorageClient(aconfig2, false);

    final BlobOutputStream blobOutputStream1 = c1.getBlobOutputStream();
    final BlobOutputStream blobOutputStream2 = c2.getBlobOutputStream();
    try (Stream<String> stream = Files.lines(Paths.get(loremIpsumShortFilePath))) {
      stream.forEach(s -> {
        blobOutputStream1.write(s.getBytes());
        blobOutputStream2.write(s.getBytes());
      });
    } finally {
      blobOutputStream1.close();
      blobOutputStream2.close();
    }

    // TODO enable when finish testing
    c1.deleteBlob();
    c2.deleteBlob();
  }
}


