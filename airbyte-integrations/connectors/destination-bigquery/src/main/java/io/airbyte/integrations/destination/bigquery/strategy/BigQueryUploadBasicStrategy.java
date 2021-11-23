package io.airbyte.integrations.destination.bigquery.strategy;

import static io.airbyte.integrations.destination.bigquery.helpers.LoggerHelper.printHeapMemoryConsumption;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.Schema;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.bigquery.BigQueryWriteConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryUploadBasicStrategy implements BigQueryUploadStrategy {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryUploadBasicStrategy.class);

  @Override
  public void upload(BigQueryWriteConfig writer, AirbyteMessage airbyteMessage, ConfiguredAirbyteCatalog catalog) {
    try {
      writer.getWriter()
          .write(ByteBuffer.wrap((Jsons.serialize(formatRecord(writer.getSchema(), airbyteMessage.getRecord())) + "\n").getBytes(Charsets.UTF_8)));
    } catch (final IOException | RuntimeException e) {
      LOGGER.error("Got an error while writing message: {}", e.getMessage(), e);
      LOGGER.error(String.format(
          "Failed to process a message for job: %s, \nStreams numbers: %s, \nSyncMode: %s, \nTableName: %s, \nTmpTableName: %s, \nAirbyteMessage: %s",
          writer.getWriter().getJob(), catalog.getStreams().size(), writer.getSyncMode(), writer.getTable(), writer.getTmpTable(),
          airbyteMessage.getRecord()));
      printHeapMemoryConsumption();
      throw new RuntimeException(e);
    }
  }

  protected JsonNode formatRecord(final Schema schema, final AirbyteRecordMessage recordMessage) {
    // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
    // use BQ helpers to string-format correctly.
    final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    final String formattedEmittedAt = QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();
    final JsonNode formattedData = StandardNameTransformer.formatJsonPath(recordMessage.getData());
    return Jsons.jsonNode(ImmutableMap.of(
        JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
        JavaBaseConstants.COLUMN_NAME_DATA, Jsons.serialize(formattedData),
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT, formattedEmittedAt));
  }
}
