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

package io.airbyte.integrations.destination.azure_blob_storage.avro;

import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.BlobOutputStream;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConfig;
import io.airbyte.integrations.destination.azure_blob_storage.writer.AzureBlobStorageWriter;
import io.airbyte.integrations.destination.azure_blob_storage.writer.BaseAzureBlobStorageWriter;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.IOException;
import java.util.UUID;
import org.apache.avro.Schema;
import org.apache.avro.file.DataFileWriter;
import org.apache.avro.generic.GenericData.Record;
import org.apache.avro.generic.GenericDatumWriter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureBlobStorageAvroWriter extends BaseAzureBlobStorageWriter implements
    AzureBlobStorageWriter {

  protected static final Logger LOGGER = LoggerFactory.getLogger(AzureBlobStorageAvroWriter.class);

  private final AvroRecordFactory avroRecordFactory;
  private final DataFileWriter<Record> dataFileWriter;
  private final BlobOutputStream blobOutputStream;

  public AzureBlobStorageAvroWriter(AzureBlobStorageDestinationConfig config,
                                    AppendBlobClient appendBlobClient,
                                    ConfiguredAirbyteStream configuredStream,
                                    boolean isNewlyCreatedBlob,
                                    Schema schema,
                                    JsonFieldNameUpdater nameUpdater)
      throws IOException {
    super(config, appendBlobClient, configuredStream);

    this.blobOutputStream = appendBlobClient.getBlobOutputStream();
    this.avroRecordFactory = new AvroRecordFactory(schema, nameUpdater);

    AzureBlobStorageAvroFormatConfig formatConfig = (AzureBlobStorageAvroFormatConfig) config
        .getFormatConfig();

    this.dataFileWriter = new DataFileWriter<>(new GenericDatumWriter<Record>())
        .setCodec(formatConfig.getCodecFactory())
        .create(schema, blobOutputStream);

    // DatumWriter writer = new ReflectDatumWriter(Record.class);
    // DataFileWriter file = new DataFileWriter(writer);
    // file.setMeta("version", 1);
    // file.setMeta("creator", "ThinkBigAnalytics");
    // file.setCodec(CodecFactory.deflateCodec(5));
    //// file.create(schema, new File("/tmp/records"));
    // file.appendTo(new File("/tmp/records"));

  }

  @Override
  public void write(UUID id, AirbyteRecordMessage recordMessage) throws IOException {
    dataFileWriter.append(avroRecordFactory.getAvroRecord(id, recordMessage));
  }

  @Override
  protected void closeWhenSucceed() throws IOException {
    dataFileWriter.close();
    // outputStream.close();
    // uploadManager.complete();
  }

  @Override
  protected void closeWhenFail() throws IOException {
    dataFileWriter.close();
    // outputStream.close();
    // uploadManager.abort();
  }

}
