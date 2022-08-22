/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryRecordConsumer.class);

  private final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private AirbyteMessage lastStateMessage = null;

  public BigQueryRecordConsumer(final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap,
                                final Consumer<AirbyteMessage> outputRecordCollector) {
    this.uploaderMap = uploaderMap;
    this.outputRecordCollector = outputRecordCollector;
  }

  @Override
  protected void startTracked() {
    // todo (cgardens) - move contents of #write into this method.
  }

  @Override
  public void acceptTracked(final AirbyteMessage message) {
    if (message.getType() == Type.STATE) {
      lastStateMessage = message;
      outputRecordCollector.accept(message);
    } else if (message.getType() == Type.RECORD) {
      processRecord(message);
    } else {
      LOGGER.warn("Unexpected message: {}", message.getType());
    }
  }

  private void processRecord(final AirbyteMessage message) {
    final var pair = AirbyteStreamNameNamespacePair.fromRecordMessage(message.getRecord());
    uploaderMap.get(pair).upload(message);
  }

  @Override
  public void close(final boolean hasFailed) {
    LOGGER.info("Started closing all connections");
    final List<Exception> exceptionsThrown = new ArrayList<>();
    uploaderMap.values().forEach(uploader -> {
      try {
        uploader.close(hasFailed, outputRecordCollector, lastStateMessage);
      } catch (final Exception e) {
        exceptionsThrown.add(e);
        LOGGER.error("Exception while closing uploader {}", uploader, e);
      }
    });
    if (!exceptionsThrown.isEmpty()) {
      throw new RuntimeException(String.format("Exceptions thrown while closing consumer: %s", Strings.join(exceptionsThrown, "\n")));
    }
  }

}
