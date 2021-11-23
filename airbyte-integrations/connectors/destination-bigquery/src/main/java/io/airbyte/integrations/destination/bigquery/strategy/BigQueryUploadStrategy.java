package io.airbyte.integrations.destination.bigquery.strategy;

import io.airbyte.integrations.destination.bigquery.BigQueryWriteConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

public interface BigQueryUploadStrategy {

  void upload(BigQueryWriteConfig writer, AirbyteMessage airbyteMessage, ConfiguredAirbyteCatalog catalog);
}
