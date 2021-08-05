/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;

public class AzureBlobStorageConnectionCheckerIntegrationTest {

  protected final String secretFilePath = "secrets/config.json";
  // TODO fix file path!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  protected final String loremIpsumShortFilePath =
      "/home/ievgeniit/Code/airbyte/airbyte-integrations/connectors/destination-azure-blob-storage/src/main/resources/LoremIpsumShort.txt";
  private AzureBlobStorageDestinationConfig azureBlobStorageConfig;

  @BeforeEach
  public void beforeAll() {
    final JsonNode configFomSecrets = Jsons.deserialize(IOs.readFile(Path.of(secretFilePath)));
    JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", configFomSecrets.get("azure_blob_storage_account_name"))
        .put("azure_blob_storage_account_key", configFomSecrets.get("azure_blob_storage_account_key"))
        .put("azure_blob_storage_endpoint_domain_name", configFomSecrets.get("azure_blob_storage_endpoint_domain_name"))
        .put("format", getJsonlFormatConfig())
        .build());

    azureBlobStorageConfig = AzureBlobStorageDestinationConfig
        .getAzureBlobStorageConfig(config);
  }

  // @Test
  // public void testSingleRun() {
  // AzureBlobStorageClient c = new AzureBlobStorageClient(azureBlobStorageConfig, false);
  // c.writeUsingAppendBlock("Some test text to write");
  //
  // PagedIterable<BlobItem> blobItems = c.listBlobsInContainer();
  // Optional<BlobItem> first = blobItems.stream()
  // .filter(blobItem -> blobItem.getName().equals(azureBlobStorageConfig.getBlobName()))
  // .findFirst();
  //
  // c.deleteBlob();
  //
  // assertTrue(first.isPresent());
  // assertEquals(azureBlobStorageConfig.getBlobName(), first.get().getName());
  // }

  // @Test
  // public void testUploadFromFileRun() throws IOException {
  //
  // AzureBlobStorageDestinationConfig aconfig1 = new AzureBlobStorageDestinationConfig(
  // azureBlobStorageConfig.getEndpointUrl(),
  // azureBlobStorageConfig.getAccountName(),
  // azureBlobStorageConfig.getAccountKey(),
  // "containernameforthread",
  // "blobname1file" + System.currentTimeMillis());
  //
  // AzureBlobStorageClient c1 = new AzureBlobStorageClient(aconfig1, false);
  //
  // byte[] bytes = Files.readAllBytes(Paths.get(loremIpsumShortFilePath));
  //
  // BlobOutputStream blobOutputStream = c1.getBlobOutputStream();
  // blobOutputStream.write(bytes);
  // blobOutputStream.close();
  //
  // // TODO enable when finish testing
  // c1.deleteBlob();
  //
  // }

  // @Test
  // public void test2simultaneousRun() throws IOException {
  //
  // AzureBlobStorageDestinationConfig aconfig1 = new AzureBlobStorageDestinationConfig(
  // azureBlobStorageConfig.getEndpointUrl(),
  // azureBlobStorageConfig.getAccountName(),
  // azureBlobStorageConfig.getAccountKey(),
  // "containernameforthread",
  // "blobname1" + System.currentTimeMillis());
  //
  // AzureBlobStorageClient c1 = new AzureBlobStorageClient(aconfig1, false);
  //
  // AzureBlobStorageDestinationConfig aconfig2 = new AzureBlobStorageDestinationConfig(
  // azureBlobStorageConfig.getEndpointUrl(),
  // azureBlobStorageConfig.getAccountName(),
  // azureBlobStorageConfig.getAccountKey(),
  // "containernameforthread",
  // "blobname1" + System.currentTimeMillis());
  //
  // AzureBlobStorageClient c2 = new AzureBlobStorageClient(aconfig2, false);
  //
  // final BlobOutputStream blobOutputStream1 = c1.getBlobOutputStream();
  // final BlobOutputStream blobOutputStream2 = c2.getBlobOutputStream();
  // try (Stream<String> stream = Files.lines(Paths.get(loremIpsumShortFilePath))) {
  // stream.forEach(s -> {
  // blobOutputStream1.write(s.getBytes());
  // blobOutputStream2.write(s.getBytes());
  // });
  // } finally {
  // blobOutputStream1.close();
  // blobOutputStream2.close();
  // }
  //
  // // TODO enable when finish testing
  // c1.deleteBlob();
  // c2.deleteBlob();
  // }

  private JsonNode getJsonlFormatConfig() {
    return Jsons.deserialize("{\n"
        + "  \"format_type\": \"JSONL\"\n"
        + "}");
  }

}
