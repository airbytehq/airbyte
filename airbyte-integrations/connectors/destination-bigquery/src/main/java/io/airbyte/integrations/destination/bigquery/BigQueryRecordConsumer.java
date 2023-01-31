/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Record Consumer used for STANDARD INSERTS
 */
public class BigQueryRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryRecordConsumer.class);

  private final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final String datasetId;
  private AirbyteMessage lastStateMessage = null;

  public BigQueryRecordConsumer(final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap,
                                final Consumer<AirbyteMessage> outputRecordCollector,
                                final String datasetId) {
    this.uploaderMap = uploaderMap;
    this.outputRecordCollector = outputRecordCollector;
    this.datasetId = datasetId;
  }

  @Override
  protected void startTracked() {
    // todo (cgardens) - move contents of #write into this method.
  }

  /**
   * Processes STATE and RECORD {@link AirbyteMessage} with all else logged as unexpected
   *
   * <li>For STATE messages emit messages back to the platform</li>
   * <li>For RECORD messages upload message to associated Airbyte Stream. This means that RECORDS will
   * be associated with their respective streams when more than one record exists</li>
   *
   * @param message {@link AirbyteMessage} to be processed
   */
  @Override
  public void acceptTracked(final AirbyteMessage message) {
    if (message.getType() == Type.STATE) {
      lastStateMessage = message;
      outputRecordCollector.accept(message);
    } else if (message.getType() == Type.RECORD) {
      if (StringUtils.isEmpty(message.getRecord().getNamespace())) {
        message.getRecord().setNamespace(datasetId);
      }
      processRecord(message);
    } else {
      LOGGER.warn("Unexpected message: {}", message.getType());
    }
  }

  /**
   * Processes {@link io.airbyte.protocol.models.AirbyteRecordMessage} by writing Airbyte stream data
   * to Big Query Writer
   *
   * @param message record to be written
   */
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
