/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pulsar;

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.apache.pulsar.client.api.Producer;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.PulsarClientException;
import org.apache.pulsar.client.api.Schema;
import org.apache.pulsar.client.api.schema.GenericRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PulsarRecordConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(PulsarRecordConsumer.class);

  private final PulsarDestinationConfig config;
  private final Map<AirbyteStreamNameNamespacePair, Producer<GenericRecord>> producerMap;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final NamingConventionTransformer nameTransformer;
  private final PulsarClient client;

  public PulsarRecordConsumer(final PulsarDestinationConfig pulsarDestinationConfig,
                              final ConfiguredAirbyteCatalog catalog,
                              final PulsarClient pulsarClient,
                              final Consumer<AirbyteMessage> outputRecordCollector,
                              final NamingConventionTransformer nameTransformer) {
    this.config = pulsarDestinationConfig;
    this.producerMap = new HashMap<>();
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
    this.nameTransformer = nameTransformer;
    this.client = pulsarClient;
  }

  @Override
  protected void startTracked() {
    producerMap.putAll(buildProducerMap());
  }

  @Override
  protected void acceptTracked(final AirbyteMessage airbyteMessage) {
    if (airbyteMessage.getType() == AirbyteMessage.Type.STATE) {
      outputRecordCollector.accept(airbyteMessage);
    } else if (airbyteMessage.getType() == AirbyteMessage.Type.RECORD) {
      final AirbyteRecordMessage recordMessage = airbyteMessage.getRecord();
      final Producer<GenericRecord> producer = producerMap.get(AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage));
      final String key = UUID.randomUUID().toString();
      final GenericRecord value = Schema.generic(PulsarDestinationConfig.getSchemaInfo())
          .newRecordBuilder()
          .set(PulsarDestination.COLUMN_NAME_AB_ID, key)
          .set(PulsarDestination.COLUMN_NAME_STREAM, recordMessage.getStream())
          .set(PulsarDestination.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt())
          .set(PulsarDestination.COLUMN_NAME_DATA, recordMessage.getData().toString().getBytes(StandardCharsets.UTF_8))
          .build();

      sendRecord(producer, value);
    } else {
      LOGGER.warn("Unexpected message: " + airbyteMessage.getType());
    }
  }

  Map<AirbyteStreamNameNamespacePair, Producer<GenericRecord>> buildProducerMap() {
    return catalog.getStreams().stream()
        .map(stream -> AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream.getStream()))
        .collect(Collectors.toMap(Function.identity(), pair -> {
          String topic = nameTransformer.getIdentifier(config.getTopicPattern()
              .replaceAll("\\{namespace}", Optional.ofNullable(pair.getNamespace()).orElse(""))
              .replaceAll("\\{stream}", Optional.ofNullable(pair.getName()).orElse("")));
          return PulsarUtils.buildProducer(client, Schema.generic(PulsarDestinationConfig.getSchemaInfo()), config.getProducerConfig(),
              config.uriForTopic(topic));
        }, (existing, newValue) -> existing));
  }

  private void sendRecord(final Producer<GenericRecord> producer, final GenericRecord record) {
    producer.sendAsync(record);
    if (config.isSync()) {
      try {
        producer.flush();
      } catch (PulsarClientException e) {
        LOGGER.error("Error sending message to topic.", e);
        throw new RuntimeException("Cannot send message to Pulsar. Error: " + e.getMessage(), e);
      }
    }
  }

  @Override
  protected void close(final boolean hasFailed) {
    producerMap.values().forEach(producer -> {
      Exceptions.swallow(producer::flush);
      Exceptions.swallow(producer::close);
    });
    Exceptions.swallow(client::close);
  }

}
