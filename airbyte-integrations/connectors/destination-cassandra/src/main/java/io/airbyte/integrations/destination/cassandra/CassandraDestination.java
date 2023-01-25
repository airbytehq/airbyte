/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

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

class CassandraDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(CassandraDestination.class);

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new CassandraDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    var cassandraConfig = new CassandraConfig(config);
    // add random uuid to avoid conflicts with existing tables.
    String tableName = "table_" + UUID.randomUUID().toString().replace("-", "");
    CassandraCqlProvider cassandraCqlProvider = null;
    try {
      cassandraCqlProvider = new CassandraCqlProvider(cassandraConfig);
      // check connection and write permissions
      cassandraCqlProvider.createKeySpaceIfNotExists(cassandraConfig.getKeyspace(),
          cassandraConfig.getReplication());
      cassandraCqlProvider.createTableIfNotExists(cassandraConfig.getKeyspace(), tableName);
      cassandraCqlProvider.insert(cassandraConfig.getKeyspace(), tableName, "{}");
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.error("Can't establish Cassandra connection with reason: ", e);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED);
    } finally {
      if (cassandraCqlProvider != null) {
        try {
          cassandraCqlProvider.dropTableIfExists(cassandraConfig.getKeyspace(), tableName);
        } catch (Exception e) {
          LOGGER.error("Error while deleting temp table {} with reason: ", tableName, e);
        }
        cassandraCqlProvider.close();
      }
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog configuredCatalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final CassandraConfig cassandraConfig = new CassandraConfig(config);
    final CassandraCqlProvider cassandraCqlProvider = new CassandraCqlProvider(cassandraConfig);
    return new CassandraMessageConsumer(cassandraConfig, configuredCatalog, cassandraCqlProvider, outputRecordCollector);
  }

}
