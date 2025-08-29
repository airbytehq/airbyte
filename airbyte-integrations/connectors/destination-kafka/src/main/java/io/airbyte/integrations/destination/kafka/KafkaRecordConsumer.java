/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.HashMap;
import java.util.List;
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
  private final Map<AirbyteStreamNameNamespacePair, List<List<String>>> primaryKeyMap;
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
    this.primaryKeyMap = new HashMap<>();
    this.producer = kafkaDestinationConfig.getProducer();
    this.sync = kafkaDestinationConfig.isSync();
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
    this.nameTransformer = nameTransformer;
  }

  @Override
  protected void startTracked() {
    topicMap.putAll(buildTopicMap());
    primaryKeyMap.putAll(buildPrimaryKeyMap());
  }

  @Override
  protected void acceptTracked(final AirbyteMessage airbyteMessage) {
    if (airbyteMessage.getType() == AirbyteMessage.Type.STATE) {
      outputRecordCollector.accept(airbyteMessage);
    } else if (airbyteMessage.getType() == AirbyteMessage.Type.RECORD) {
      final AirbyteRecordMessage recordMessage = airbyteMessage.getRecord();

      // if brokers have the property "auto.create.topics.enable" enabled then topics will be auto-created
      // otherwise these topics need to have been pre-created.
      final AirbyteStreamNameNamespacePair streamPair = AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage);
      final String topic = topicMap.get(streamPair);
      final String key = UUID.randomUUID().toString();
      
      // Build the message with required fields
      final ImmutableMap.Builder<String, Object> valueBuilder = ImmutableMap.<String, Object>builder()
          .put(KafkaDestination.COLUMN_NAME_AB_ID, key)
          .put(KafkaDestination.COLUMN_NAME_STREAM, recordMessage.getStream())
          .put(KafkaDestination.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt())
          .put(KafkaDestination.COLUMN_NAME_DATA, recordMessage.getData());
      
      // Add primary keys if available
      final List<List<String>> primaryKeys = primaryKeyMap.get(streamPair);
      if (primaryKeys != null && !primaryKeys.isEmpty()) {
        valueBuilder.put(KafkaDestination.COLUMN_NAME_PRIMARY_KEYS, primaryKeys);
      }
      
      // Add CDC operation if detected
      final String cdcOperation = extractCdcOperation(recordMessage.getData());
      if (cdcOperation != null) {
        valueBuilder.put(KafkaDestination.COLUMN_NAME_CDC_OPERATION, cdcOperation);
      }
      
      final JsonNode value = Jsons.jsonNode(valueBuilder.build());
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

  Map<AirbyteStreamNameNamespacePair, List<List<String>>> buildPrimaryKeyMap() {
    return catalog.getStreams().stream()
        .collect(Collectors.toMap(
            stream -> AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream()),
            stream -> {
              // Use user-configured primary key if available, otherwise fall back to source-defined
              final List<List<String>> primaryKey = stream.getPrimaryKey();
              if (primaryKey != null && !primaryKey.isEmpty()) {
                return primaryKey;
              }
              final List<List<String>> sourceDefinedPrimaryKey = stream.getStream().getSourceDefinedPrimaryKey();
              return sourceDefinedPrimaryKey != null ? sourceDefinedPrimaryKey : List.of();
            }));
  }

  String extractCdcOperation(final JsonNode data) {
    // Check for CDC fields to determine the operation type
    if (data.has("_ab_cdc_deleted_at") && !data.get("_ab_cdc_deleted_at").isNull()) {
      return "delete";
    } else if (data.has("_ab_cdc_updated_at") && !data.get("_ab_cdc_updated_at").isNull()) {
      return "update";
    } else if (data.has("_ab_cdc_lsn") && !data.get("_ab_cdc_lsn").isNull()) {
      return "insert";
    }
    return null; // Non-CDC sync or no operation detected
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
