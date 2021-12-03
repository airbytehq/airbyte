package io.airbyte.integrations.destination.bigquery.strategy;

import io.airbyte.integrations.destination.bigquery.BigQueryWriteConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.List;

public interface BigQueryUploadStrategy {

  void upload(BigQueryWriteConfig writer, AirbyteMessage airbyteMessage, ConfiguredAirbyteCatalog catalog);

  void close(List<BigQueryWriteConfig> writeConfigList, boolean hasFailed, AirbyteMessage lastStateMessage);
}
