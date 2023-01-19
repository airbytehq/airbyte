/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KafkaRecordConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(KafkaRecordConsumer.class);

  private final String topicPattern;
  private final Map<AirbyteStreamNameNamespacePair, String> topicMap;
  private final KafkaProducer<String, JsonNode> producer;
  private final boolean sync;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final NamingConventionTransformer nameTransformer;

  public KafkaRecordConsumer(final KafkaDestinationConfig kafkaDestinationConfig,
                             final ConfiguredAirbyteCatalog catalog,
                             final Consumer<AirbyteMessage> outputRecordCollector,
                             final NamingConventionTransformer nameTransformer) {
    this.topicPattern = kafkaDestinationConfig.getTopicPattern();
    this.topicMap = new HashMap<>();
    this.producer = kafkaDestinationConfig.getProducer();
    this.sync = kafkaDestinationConfig.isSync();
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
    this.nameTransformer = nameTransformer;
  }

  @Override
  protected void startTracked() {
    topicMap.putAll(buildTopicMap());
  }

  @Override
  protected void acceptTracked(final AirbyteMessage airbyteMessage) {
    if (airbyteMessage.getType() == AirbyteMessage.Type.STATE) {
      outputRecordCollector.accept(airbyteMessage);
    } else if (airbyteMessage.getType() == AirbyteMessage.Type.RECORD) {
      final AirbyteRecordMessage recordMessage = airbyteMessage.getRecord();

      // if brokers have the property "auto.create.topics.enable" enabled then topics will be auto-created
      // otherwise these topics need to have been pre-created.
      final String topic = topicMap.get(AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage));
      final String key = UUID.randomUUID().toString();
      final JsonNode value = Jsons.jsonNode(ImmutableMap.of(
          KafkaDestination.COLUMN_NAME_AB_ID, key,
          KafkaDestination.COLUMN_NAME_STREAM, recordMessage.getStream(),
          KafkaDestination.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt(),
          KafkaDestination.COLUMN_NAME_DATA, recordMessage.getData()));

      sendRecord(new ProducerRecord<>(topic, key, value));
    } else {
      LOGGER.warn("Unexpected message: " + airbyteMessage.getType());
    }
  }

  Map<AirbyteStreamNameNamespacePair, String> buildTopicMap() {
    return catalog.getStreams().stream()
        .map(stream -> AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream()))
        .collect(Collectors.toMap(Function.identity(),
            pair -> nameTransformer.getIdentifier(topicPattern
                .replaceAll("\\{namespace}", Optional.ofNullable(pair.getNamespace()).orElse(""))
                .replaceAll("\\{stream}", Optional.ofNullable(pair.getName()).orElse("")))));
  }

  private void sendRecord(final ProducerRecord<String, JsonNode> record) {
    producer.send(record, (recordMetadata, exception) -> {
      if (exception != null) {
        LOGGER.error("Error sending message to topic.", exception);
        throw new RuntimeException("Cannot send message to Kafka. Error: " + exception.getMessage(), exception);
      }
    });
    if (sync) {
      producer.flush();
    }
  }

  @Override
  protected void close(final boolean hasFailed) {
    producer.flush();
    producer.close();
  }

}
