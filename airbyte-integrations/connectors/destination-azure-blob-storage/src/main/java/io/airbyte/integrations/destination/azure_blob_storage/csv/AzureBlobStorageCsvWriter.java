/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.csv;

import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConfig;
import io.airbyte.integrations.destination.azure_blob_storage.writer.AzureBlobStorageWriter;
import io.airbyte.integrations.destination.azure_blob_storage.writer.BaseAzureBlobStorageWriter;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.io.BufferedOutputStream;
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
  private final BufferedOutputStream blobOutputStream;

  public AzureBlobStorageCsvWriter(final AzureBlobStorageDestinationConfig config,
                                   final AppendBlobClient appendBlobClient,
                                   final ConfiguredAirbyteStream configuredStream)
      throws IOException {
    super(config, appendBlobClient, configuredStream);

    final AzureBlobStorageCsvFormatConfig formatConfig = (AzureBlobStorageCsvFormatConfig) config
        .getFormatConfig();

    this.csvSheetGenerator = CsvSheetGenerator.Factory
        .create(configuredStream.getStream().getJsonSchema(),
            formatConfig);

    this.blobOutputStream = new BufferedOutputStream(appendBlobClient.getBlobOutputStream(), config.getOutputStreamBufferSize());

    final PrintWriter printWriter = new PrintWriter(blobOutputStream, false, StandardCharsets.UTF_8);
    this.csvPrinter = new CSVPrinter(printWriter, CSVFormat.DEFAULT.withQuoteMode(QuoteMode.ALL)
        .withHeader(csvSheetGenerator.getHeaderRow().toArray(new String[0])));
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage) throws IOException {
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
