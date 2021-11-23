package io.airbyte.integrations.destination.bigquery.strategy;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.QueryParameterValue;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.bigquery.BigQueryWriteConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryUploadGCSStrategy implements BigQueryUploadStrategy {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryUploadGCSStrategy.class);

  @Override
  public void upload(BigQueryWriteConfig writer, AirbyteMessage airbyteMessage, ConfiguredAirbyteCatalog catalog) {
    var airbyteRecordMessage = airbyteMessage.getRecord();
    var gcsCsvWriter = writer.getGcsCsvWriter();
    // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
    // use BQ helpers to string-format correctly.
    final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(airbyteRecordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    final String formattedEmittedAt = QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();
    final JsonNode formattedData = StandardNameTransformer.formatJsonPath(airbyteRecordMessage.getData());
    try {
      gcsCsvWriter.getCsvPrinter().printRecord(
          UUID.randomUUID().toString(),
          formattedEmittedAt,
          Jsons.serialize(formattedData));
    } catch (IOException e) {
      e.printStackTrace();
      LOGGER.warn("An error occurred writing CSV file.");
    }
  }
}
