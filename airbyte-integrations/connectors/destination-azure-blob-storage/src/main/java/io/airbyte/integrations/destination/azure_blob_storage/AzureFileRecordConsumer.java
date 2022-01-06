/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.azure_blob_storage.file.uploader.AbstractAzureUploader;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.function.Consumer;

public class AzureFileRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureFileRecordConsumer.class);

  private final Map<AirbyteStreamNameNamespacePair, AbstractAzureUploader<?>> uploaderMap;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private AirbyteMessage lastStateMessage = null;

  public AzureFileRecordConsumer(final Map<AirbyteStreamNameNamespacePair, AbstractAzureUploader<?>> uploaderMap,
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
    } else if (message.getType() == Type.RECORD) {
      processRecord(message);
    } else {
      LOGGER.warn("Unexpected message: {}", message.getType());
    }
  }

  private void processRecord(AirbyteMessage message) {
    final var pair = AirbyteStreamNameNamespacePair.fromRecordMessage(message.getRecord());
    uploaderMap.get(pair).upload(message);
  }

  @Override
  public void close(final boolean hasFailed) {
    LOGGER.info("Started closing all connections");
    uploaderMap.values().parallelStream().forEach(uploader -> uploader.close(hasFailed, outputRecordCollector, lastStateMessage));
  }

}
