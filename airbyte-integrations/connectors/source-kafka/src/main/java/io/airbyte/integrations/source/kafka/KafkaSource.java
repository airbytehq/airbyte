/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import com.google.common.collect.Lists;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KafkaSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(KafkaSource.class);

  public KafkaSource() {}

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final String testTopic = config.has("test_topic") ? config.get("test_topic").asText() : "";
      if (!testTopic.isBlank()) {
        final KafkaSourceConfig kafkaSourceConfig = KafkaSourceConfig.getKafkaSourceConfig(config);
        final KafkaConsumer<String, JsonNode> consumer = kafkaSourceConfig.getCheckConsumer();
        consumer.subscribe(Pattern.compile(testTopic));
        consumer.listTopics();
        consumer.close();
        LOGGER.info("Successfully connected to Kafka brokers for topic '{}'.", config.get("test_topic").asText());
      }
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to connect to the Kafka brokers: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect to the Kafka brokers with provided configuration. \n" + e.getMessage());
    }
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) throws Exception {

    final Set<String> topicsToSubscribe = KafkaSourceConfig.getKafkaSourceConfig(config).getTopicsToSubscribe();
    final List<AirbyteStream> streams = topicsToSubscribe.stream().map(topic -> CatalogHelpers
        .createAirbyteStream(topic, Field.of("value", JsonSchemaType.STRING))
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))
        .collect(Collectors.toList());
    return new AirbyteCatalog().withStreams(streams);
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final JsonNode state)
      throws Exception {
    final AirbyteConnectionStatus check = check(config);
    if (check.getStatus().equals(AirbyteConnectionStatus.Status.FAILED)) {
      throw new RuntimeException("Unable establish a connection: " + check.getMessage());
    }

    final KafkaSourceConfig kafkaSourceConfig = KafkaSourceConfig.getKafkaSourceConfig(config);
    final KafkaConsumer<String, JsonNode> consumer = kafkaSourceConfig.getConsumer();
    final List<ConsumerRecord<String, JsonNode>> recordsList = new ArrayList<>();

    final int retry = config.has("repeated_calls") ? config.get("repeated_calls").intValue() : 0;
    int pollCount = 0;
    final int polling_time = config.has("polling_time") ? config.get("polling_time").intValue() : 100;
    while (true) {
      final ConsumerRecords<String, JsonNode> consumerRecords = consumer.poll(Duration.of(polling_time, ChronoUnit.MILLIS));
      if (consumerRecords.count() == 0) {
        pollCount++;
        if (pollCount > retry) {
          break;
        }
      }

      consumerRecords.forEach(record -> {
        LOGGER.info("Consumer Record: key - {}, value - {}, partition - {}, offset - {}",
            record.key(), record.value(), record.partition(), record.offset());
        recordsList.add(record);
      });
      consumer.commitAsync();
    }
    consumer.close();
    final Iterator<ConsumerRecord<String, JsonNode>> iterator = recordsList.iterator();

    return AutoCloseableIterators.fromIterator(new AbstractIterator<>() {

      @Override
      protected AirbyteMessage computeNext() {
        if (iterator.hasNext()) {
          final ConsumerRecord<String, JsonNode> record = iterator.next();
          return new AirbyteMessage()
              .withType(AirbyteMessage.Type.RECORD)
              .withRecord(new AirbyteRecordMessage()
                  .withStream(record.topic())
                  .withEmittedAt(Instant.now().toEpochMilli())
                  .withData(record.value()));
        }

        return endOfData();
      }

    });
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new KafkaSource();
    LOGGER.info("Starting source: {}", KafkaSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("Completed source: {}", KafkaSource.class);
  }

}
