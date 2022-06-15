/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class CassandraMessageConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(CassandraMessageConsumer.class);

  private final CassandraConfig cassandraConfig;

  private final Consumer<AirbyteMessage> outputRecordCollector;

  private final Map<AirbyteStreamNameNamespacePair, CassandraStreamConfig> cassandraStreams;

  private final CassandraCqlProvider cassandraCqlProvider;

  private AirbyteMessage lastMessage = null;

  public CassandraMessageConsumer(CassandraConfig cassandraConfig,
                                  ConfiguredAirbyteCatalog configuredCatalog,
                                  Consumer<AirbyteMessage> outputRecordCollector) {
    this.cassandraConfig = cassandraConfig;
    this.outputRecordCollector = outputRecordCollector;
    this.cassandraCqlProvider = new CassandraCqlProvider(cassandraConfig);
    var nameTransformer = new CassandraNameTransformer(cassandraConfig);
    this.cassandraStreams = configuredCatalog.getStreams().stream()
        .collect(Collectors.toUnmodifiableMap(
            AirbyteStreamNameNamespacePair::fromConfiguredAirbyteSteam,
            k -> new CassandraStreamConfig(
                nameTransformer.outputKeyspace(k.getStream().getNamespace()),
                nameTransformer.outputTable(k.getStream().getName()),
                nameTransformer.outputTmpTable(k.getStream().getName()),
                k.getDestinationSyncMode())));
  }

  @Override
  protected void startTracked() {
    cassandraStreams.forEach((k, v) -> {
      cassandraCqlProvider.createKeySpaceIfNotExists(v.getKeyspace(), cassandraConfig.getReplication());
      cassandraCqlProvider.createTableIfNotExists(v.getKeyspace(), v.getTempTableName());
    });
  }

  @Override
  protected void acceptTracked(AirbyteMessage message) {
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      var messageRecord = message.getRecord();
      var streamConfig =
          cassandraStreams.get(AirbyteStreamNameNamespacePair.fromRecordMessage(messageRecord));
      if (streamConfig == null) {
        throw new IllegalArgumentException("Unrecognized destination stream");
      }
      var data = Jsons.serialize(messageRecord.getData());
      cassandraCqlProvider.insert(streamConfig.getKeyspace(), streamConfig.getTempTableName(), data);
    } else if (message.getType() == AirbyteMessage.Type.STATE) {
      this.lastMessage = message;
    } else {
      LOGGER.warn("Unsupported airbyte message type: {}", message.getType());
    }
  }

  @Override
  protected void close(boolean hasFailed) {
    if (!hasFailed) {
      cassandraStreams.forEach((k, v) -> {
        try {
          cassandraCqlProvider.createTableIfNotExists(v.getKeyspace(), v.getTableName());
          switch (v.getDestinationSyncMode()) {
            case APPEND -> {
              cassandraCqlProvider.copy(v.getKeyspace(), v.getTempTableName(), v.getTableName());
            }
            case OVERWRITE -> {
              cassandraCqlProvider.truncate(v.getKeyspace(), v.getTableName());
              cassandraCqlProvider.copy(v.getKeyspace(), v.getTempTableName(), v.getTableName());
            }
            default -> throw new UnsupportedOperationException();
          }
        } catch (Exception e) {
          LOGGER.error("Error while copying data to table {}: : ", v.getTableName(), e);
        }
      });
      outputRecordCollector.accept(lastMessage);
    }

    cassandraStreams.forEach((k, v) -> {
      try {
        cassandraCqlProvider.dropTableIfExists(v.getKeyspace(), v.getTempTableName());
      } catch (Exception e) {
        LOGGER.error("Error while deleting temp table {} with reason: ", v.getTempTableName(), e);
      }
    });
    cassandraCqlProvider.close();

  }

}
