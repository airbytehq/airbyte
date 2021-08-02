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

import com.azure.core.http.rest.PagedIterable;
import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.models.BlobItem;
import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.BlobOutputStream;
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.azure.storage.common.StorageSharedKeyCredential;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Deprecated
public class AzureBlobStorageClient {

  private final BlobContainerClient containerClient; // schema in SQL DBs controller
  private final AppendBlobClient storageClient; // aka "SQL Table" controller
  private final boolean overwriteDataInStream;

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureBlobStorageClient.class);

  public AzureBlobStorageClient(AzureBlobStorageDestinationConfig azureBlobStorageConfig,
                                boolean overwriteDataInStream) {

    this.overwriteDataInStream = overwriteDataInStream;

    StorageSharedKeyCredential credential = new StorageSharedKeyCredential(
        azureBlobStorageConfig.getAccountName(),
        azureBlobStorageConfig.getAccountKey());
    storageClient =
        new SpecializedBlobClientBuilder()
            .endpoint(azureBlobStorageConfig.getEndpointUrl())
            .credential(credential)
            .containerName(azureBlobStorageConfig.getContainerName()) // Like schema in DB
            .blobName(azureBlobStorageConfig.getBlobName()) // Like table in DB
            .buildAppendBlobClient();

    // create container if absent (aka SQl Schema)
    this.containerClient = storageClient.getContainerClient();
    if (!containerClient.exists()) {
      containerClient.create();
    }

    // create a storage container if absent (aka Table is SQL BD)
    if (!storageClient.exists()) {
      storageClient.create(overwriteDataInStream);
      LOGGER.debug("blobContainerClient created");
    } else {
      LOGGER.debug("blobContainerClient already exists");
    }
  }

  public BlobOutputStream getBlobOutputStream() {
    return storageClient.getBlobOutputStream();
  }

  // TODO !!!!!!!!!!!!!!!fails for empty lines !!!!!!!!!!!!!!!!!!!!!!!!!
  // this options may be used to write and flush right away.
  public void writeUsingAppendBlock(String data) {
    LOGGER.debug("Writing data to Azure Blob storage: " + data);
    if (overwriteDataInStream) {
      LOGGER.debug("Override option is enabled. Old data is will be removed");
      storageClient.delete();
      storageClient.create();
    }
    InputStream dataStream = new ByteArrayInputStream(data.getBytes(StandardCharsets.UTF_8));

    Integer blobCommittedBlockCount = storageClient.appendBlock(dataStream, data.length())
        .getBlobCommittedBlockCount();

    LOGGER.debug("blobCommittedBlockCount: " + blobCommittedBlockCount);
  }

  public void writeUsingStreams(List<String> strings) throws IOException {
    LOGGER.debug("Writing data to Azure Blob storage: " + strings);
    if (overwriteDataInStream) {
      LOGGER.debug("Override option is enbaled. Old data is will be removed");
      storageClient.delete();
      storageClient.create();
    }

    final BlobOutputStream blobOutputStream = storageClient.getBlobOutputStream();

    strings.forEach(
        s -> {
          blobOutputStream.write((s + "\n").getBytes());
        });

    blobOutputStream.close();
  }

  public void writeUsingStreams(String data) throws IOException {
    LOGGER.debug("Writing data to Azure Blob storage: " + data);
    if (overwriteDataInStream) {
      LOGGER.debug("Override option is enbaled. Old data is will be removed");
      storageClient.delete();
      storageClient.create();
    }

    final BlobOutputStream blobOutputStream = storageClient.getBlobOutputStream();

    blobOutputStream.write((data).getBytes());
    // blobOutputStream.write((data + "\n").getBytes());

    blobOutputStream.flush();
    blobOutputStream.close();
  }

  /*
   * List the blob(s) in our container.
   */
  public PagedIterable<BlobItem> listBlobsInContainer() {
    return containerClient.listBlobs();

  }

  /*
   * Delete the blob we created earlier.
   */
  public void deleteBlob() {
    LOGGER.info("Deleting blob: " + storageClient.getBlobName());
    storageClient.delete(); // remove aka "SQL Table" used
  }

  /*
   * Delete the Container. Be very careful when you ise ir. It removes thw whole bucket and supposed
   * to be used in check connection ony for writing tmp data
   *
   */
  public void deleteContainer() {
    LOGGER.info("Deleting blob: " + containerClient.getBlobContainerName());
    containerClient.delete(); // remove aka "SQL Schema" used
  }

  // this a kinda test method that is used in CHECK operation to make sure all works fine with the
  // currect config
  public void attemptWriteAndDelete() throws IOException {
    // List<String> strings = Arrays.asList("Test12", "Test22", "Test32", null);
    // writeUsingStreams(strings);

    writeUsingAppendBlock("Some test data");
    listBlobsInContainer()
        .forEach(
            blobItem -> LOGGER.debug(
                "Blob name: " + blobItem.getName() + "Snapshot: " + blobItem.getSnapshot()));

    deleteBlob();
  }

}
