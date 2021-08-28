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

package io.airbyte.integrations.destination.azure_blob_storage.jsonl;

import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.BlobOutputStream;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConfig;
import io.airbyte.integrations.destination.azure_blob_storage.writer.AzureBlobStorageWriter;
import io.airbyte.integrations.destination.azure_blob_storage.writer.BaseAzureBlobStorageWriter;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureBlobStorageJsonlWriter extends BaseAzureBlobStorageWriter implements
    AzureBlobStorageWriter {

  protected static final Logger LOGGER = LoggerFactory.getLogger(AzureBlobStorageJsonlWriter.class);

  private static final ObjectMapper MAPPER = MoreMappers.initMapper();
  private static final ObjectWriter WRITER = MAPPER.writer();

  private final BlobOutputStream blobOutputStream;
  private final PrintWriter printWriter;

  public AzureBlobStorageJsonlWriter(AzureBlobStorageDestinationConfig config,
                                     AppendBlobClient appendBlobClient,
                                     ConfiguredAirbyteStream configuredStream,
                                     boolean isNewlyCreatedBlob) {
    super(config, appendBlobClient, configuredStream);
    // at this moment we already receive appendBlobClient initialized
    this.blobOutputStream = appendBlobClient.getBlobOutputStream();
    this.printWriter = new PrintWriter(blobOutputStream, true, StandardCharsets.UTF_8);
  }

  @Override
  public void write(UUID id, AirbyteRecordMessage recordMessage) {
    ObjectNode json = MAPPER.createObjectNode();
    json.put(JavaBaseConstants.COLUMN_NAME_AB_ID, id.toString());
    json.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt());
    json.set(JavaBaseConstants.COLUMN_NAME_DATA, recordMessage.getData());
    printWriter.println(Jsons.serialize(json));
  }

  @Override
  protected void closeWhenSucceed() throws IOException {
    // this would also close the blobOutputStream
    printWriter.close();
  }

  @Override
  protected void closeWhenFail() throws IOException {
    // this would also close the blobOutputStream
    printWriter.close();
  }

}
