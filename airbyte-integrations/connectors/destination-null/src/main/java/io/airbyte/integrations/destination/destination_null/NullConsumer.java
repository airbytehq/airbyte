package io.airbyte.integrations.destination.destination_null;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.destination_null.logger.NullDestinationLogger;
import io.airbyte.integrations.destination.destination_null.logger.NullDestinationLoggerFactory;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;

public class NullConsumer extends FailureTrackingAirbyteMessageConsumer {

  private final NullDestinationLoggerFactory loggerFactory;
  private final ConfiguredAirbyteCatalog configuredCatalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final Map<AirbyteStreamNameNamespacePair, NullDestinationLogger> loggers;

  private AirbyteMessage lastStateMessage = null;

  public NullConsumer(NullDestinationLoggerFactory loggerFactory,
                      ConfiguredAirbyteCatalog configuredCatalog,
                      Consumer<AirbyteMessage> outputRecordCollector) {
    this.loggerFactory = loggerFactory;
    this.configuredCatalog = configuredCatalog;
    this.outputRecordCollector = outputRecordCollector;
    this.loggers = new HashMap<>();
  }

  @Override
  protected void startTracked() {
    for (ConfiguredAirbyteStream configuredStream : configuredCatalog.getStreams()) {
      final AirbyteStream stream = configuredStream.getStream();
      final AirbyteStreamNameNamespacePair streamNamePair = AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream);
      final NullDestinationLogger logger = loggerFactory.create(streamNamePair);
      loggers.put(streamNamePair, logger);
    }
  }

  @Override
  protected void acceptTracked(AirbyteMessage airbyteMessage) {
    if (airbyteMessage.getType() == Type.STATE) {
      this.lastStateMessage = airbyteMessage;
      return;
    } else if (airbyteMessage.getType() != Type.RECORD) {
      return;
    }

    AirbyteRecordMessage recordMessage = airbyteMessage.getRecord();
    AirbyteStreamNameNamespacePair pair = AirbyteStreamNameNamespacePair
        .fromRecordMessage(recordMessage);

    if (!loggers.containsKey(pair)) {
      throw new IllegalArgumentException(
          String.format(
              "Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
              Jsons.serialize(configuredCatalog), Jsons.serialize(recordMessage)));
    }

    loggers.get(pair).log(recordMessage);
  }

  @Override
  protected void close(boolean hasFailed) {
    if (!hasFailed) {
      outputRecordCollector.accept(lastStateMessage);
    }
  }

}
