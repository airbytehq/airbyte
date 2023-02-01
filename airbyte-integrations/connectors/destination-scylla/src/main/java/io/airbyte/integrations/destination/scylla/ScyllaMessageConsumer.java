/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ScyllaMessageConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(ScyllaMessageConsumer.class);

  private final ScyllaConfig scyllaConfig;

  private final Consumer<AirbyteMessage> outputRecordCollector;

  private final Map<AirbyteStreamNameNamespacePair, ScyllaStreamConfig> scyllaStreams;

  private final ScyllaCqlProvider scyllaCqlProvider;

  public ScyllaMessageConsumer(ScyllaConfig scyllaConfig,
                               ConfiguredAirbyteCatalog configuredCatalog,
                               Consumer<AirbyteMessage> outputRecordCollector) {
    this.scyllaConfig = scyllaConfig;
    this.outputRecordCollector = outputRecordCollector;
    this.scyllaCqlProvider = new ScyllaCqlProvider(scyllaConfig);
    var nameTransformer = new ScyllaNameTransformer(scyllaConfig);
    this.scyllaStreams = configuredCatalog.getStreams().stream()
        .collect(Collectors.toUnmodifiableMap(
            AirbyteStreamNameNamespacePair::fromConfiguredAirbyteSteam,
            k -> new ScyllaStreamConfig(
                nameTransformer.outputKeyspace(k.getStream().getNamespace()),
                nameTransformer.outputTable(k.getStream().getName()),
                nameTransformer.outputTmpTable(k.getStream().getName()),
                k.getDestinationSyncMode())));
  }

  @Override
  protected void startTracked() {
    scyllaStreams.forEach((k, v) -> {
      scyllaCqlProvider.createKeyspaceIfNotExists(v.getKeyspace());
      scyllaCqlProvider.createTableIfNotExists(v.getKeyspace(), v.getTempTableName());
    });
  }

  @Override
  protected void acceptTracked(AirbyteMessage message) {
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      var messageRecord = message.getRecord();
      var streamConfig =
          scyllaStreams.get(AirbyteStreamNameNamespacePair.fromRecordMessage(messageRecord));
      if (streamConfig == null) {
        throw new IllegalArgumentException("Unrecognized destination stream");
      }
      var data = Jsons.serialize(messageRecord.getData());
      scyllaCqlProvider.insert(streamConfig.getKeyspace(), streamConfig.getTempTableName(), data);
    } else if (message.getType() == AirbyteMessage.Type.STATE) {
      outputRecordCollector.accept(message);
    } else {
      LOGGER.warn("Unsupported airbyte message type: {}", message.getType());
    }
  }

  @Override
  protected void close(boolean hasFailed) {
    if (!hasFailed) {
      scyllaStreams.forEach((k, v) -> {
        try {
          scyllaCqlProvider.createTableIfNotExists(v.getKeyspace(), v.getTableName());
          switch (v.getDestinationSyncMode()) {
            case APPEND -> {
              scyllaCqlProvider.copy(v.getKeyspace(), v.getTempTableName(), v.getTableName());
            }
            case OVERWRITE -> {
              scyllaCqlProvider.truncate(v.getKeyspace(), v.getTableName());
              scyllaCqlProvider.copy(v.getKeyspace(), v.getTempTableName(), v.getTableName());
            }
            default -> throw new UnsupportedOperationException("Unsupported destination sync mode");
          }
        } catch (Exception e) {
          LOGGER.error("Error while copying data to table {}: ", v.getTableName(), e);
        }
      });
    }

    scyllaStreams.forEach((k, v) -> {
      try {
        scyllaCqlProvider.dropTableIfExists(v.getKeyspace(), v.getTempTableName());
      } catch (Exception e) {
        LOGGER.error("Error while deleting temp table {} with reason: ", v.getTempTableName(), e);
      }
    });
    scyllaCqlProvider.close();
  }

}
