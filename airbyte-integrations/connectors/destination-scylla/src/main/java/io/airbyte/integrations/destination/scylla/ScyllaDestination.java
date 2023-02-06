/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.UUID;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ScyllaDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ScyllaDestination.class);

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new ScyllaDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    var scyllaConfig = new ScyllaConfig(config);
    // add random uuid to avoid conflicts with existing tables.
    String tableName = "table_" + UUID.randomUUID().toString().replace("-", "");
    ScyllaCqlProvider scyllaCqlProvider = null;
    try {
      scyllaCqlProvider = new ScyllaCqlProvider(scyllaConfig);
      // check connection and write permissions
      scyllaCqlProvider.createKeyspaceIfNotExists(scyllaConfig.getKeyspace());
      scyllaCqlProvider.createTableIfNotExists(scyllaConfig.getKeyspace(), tableName);
      scyllaCqlProvider.insert(scyllaConfig.getKeyspace(), tableName, "{}");
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.error("Can't establish Scylla connection with reason: ", e);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED);
    } finally {
      if (scyllaCqlProvider != null) {
        try {
          scyllaCqlProvider.dropTableIfExists(scyllaConfig.getKeyspace(), tableName);
        } catch (Exception e) {
          LOGGER.error("Error while deleting temp table {} with reason: ", tableName, e);
        }
        scyllaCqlProvider.close();
      }
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog configuredCatalog,
                                            Consumer<AirbyteMessage> outputRecordCollector) {
    return new ScyllaMessageConsumer(new ScyllaConfig(config), configuredCatalog, outputRecordCollector);
  }

}
