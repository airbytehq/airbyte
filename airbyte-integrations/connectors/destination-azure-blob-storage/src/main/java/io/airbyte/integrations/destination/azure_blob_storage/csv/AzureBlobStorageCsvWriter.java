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

package io.airbyte.integrations.destination.azure_blob_storage.csv;

import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.BlobOutputStream;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConfig;
import io.airbyte.integrations.destination.azure_blob_storage.writer.AzureBlobStorageWriter;
import io.airbyte.integrations.destination.azure_blob_storage.writer.BaseAzureBlobStorageWriter;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.QuoteMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureBlobStorageCsvWriter extends BaseAzureBlobStorageWriter implements
    AzureBlobStorageWriter {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureBlobStorageCsvWriter.class);

  private final CsvSheetGenerator csvSheetGenerator;
  private final CSVPrinter csvPrinter;
  private final BlobOutputStream blobOutputStream;

  public AzureBlobStorageCsvWriter(AzureBlobStorageDestinationConfig config,
                                   AppendBlobClient appendBlobClient,
                                   ConfiguredAirbyteStream configuredStream,
                                   boolean isNewlyCreatedBlob)
      throws IOException {
    super(config, appendBlobClient, configuredStream);

    AzureBlobStorageCsvFormatConfig formatConfig = (AzureBlobStorageCsvFormatConfig) config
        .getFormatConfig();

    this.csvSheetGenerator = CsvSheetGenerator.Factory
        .create(configuredStream.getStream().getJsonSchema(),
            formatConfig);

    this.blobOutputStream = appendBlobClient.getBlobOutputStream();

    if (isNewlyCreatedBlob) {
      this.csvPrinter = new CSVPrinter(
          new PrintWriter(blobOutputStream, true, StandardCharsets.UTF_8),
          CSVFormat.DEFAULT.withQuoteMode(QuoteMode.ALL)
              .withHeader(csvSheetGenerator.getHeaderRow().toArray(new String[0])));
    } else {
      // no header required for append
      this.csvPrinter = new CSVPrinter(
          new PrintWriter(blobOutputStream, true, StandardCharsets.UTF_8),
          CSVFormat.DEFAULT.withQuoteMode(QuoteMode.ALL));
    }
  }

  @Override
  public void write(UUID id, AirbyteRecordMessage recordMessage) throws IOException {
    csvPrinter.printRecord(csvSheetGenerator.getDataRow(id, recordMessage));
  }

  @Override
  protected void closeWhenSucceed() throws IOException {
    LOGGER.info("Closing csvPrinter when succeed");
    csvPrinter.close();
  }

  @Override
  protected void closeWhenFail() throws IOException {
    LOGGER.info("Closing csvPrinter when failed");
    csvPrinter.close();
  }

}
