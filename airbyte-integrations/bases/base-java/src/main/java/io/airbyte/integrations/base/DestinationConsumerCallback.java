package io.airbyte.integrations.base;

import io.airbyte.commons.lang.CloseableQueue;
import java.util.Map;

public interface DestinationConsumerCallback {

  void writeQuery(int batchSize, CloseableQueue<byte[]> writeBuffer, String schemaName, String tmpTableName);

  void commitRawTables(Map<String, WriteConfig> writeConfigs);

  void cleanupTmpTables(Map<String, WriteConfig> writeConfigs);
}
