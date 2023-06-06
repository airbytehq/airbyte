/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.format;
import io.airbyte.integrations.source.kafka.MessageFormat;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.AbstractIterator;
import com.google.common.collect.Lists;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.kafka.KafkaStrategy;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.*;
import io.confluent.kafka.schemaregistry.avro.AvroSchemaProvider;
import io.confluent.kafka.schemaregistry.client.CachedSchemaRegistryClient;
import io.confluent.kafka.schemaregistry.client.SchemaMetadata;
import io.confluent.kafka.schemaregistry.client.SchemaRegistryClient;
import io.confluent.kafka.schemaregistry.client.SchemaRegistryClientConfig;
import io.confluent.kafka.schemaregistry.client.rest.RestService;
import io.confluent.kafka.schemaregistry.client.rest.exceptions.RestClientException;
import io.confluent.kafka.serializers.KafkaAvroDeserializer;
import io.confluent.kafka.serializers.KafkaAvroDeserializerConfig;
import io.confluent.kafka.serializers.KafkaAvroSerializerConfig;

import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.apache.avro.Schema;
import org.apache.avro.generic.GenericRecord;
import org.apache.commons.lang3.StringUtils;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AvroFormat extends AbstractFormat {

  private static final Logger LOGGER = LoggerFactory.getLogger(AvroFormat.class);

  private KafkaConsumer<String, GenericRecord> consumer;

  public AvroFormat(JsonNode jsonConfig) {
    super(jsonConfig);
  }

  @Override
  protected Map<String, Object> getKafkaConfig() {
    Map<String, Object> properties =  super.getKafkaConfig();
    final JsonNode avro_config = config.get("MessageFormat");
    properties.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
    properties.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, KafkaAvroDeserializer.class.getName());
    properties.put(SchemaRegistryClientConfig.BASIC_AUTH_CREDENTIALS_SOURCE, "USER_INFO");
    properties.put(SchemaRegistryClientConfig.USER_INFO_CONFIG,
            String.format("%s:%s", avro_config.get("schema_registry_username").asText(), avro_config.get("schema_registry_password").asText()));
    properties.put(KafkaAvroDeserializerConfig.SCHEMA_REGISTRY_URL_CONFIG, avro_config.get("schema_registry_url").asText());
    properties.put(KafkaAvroSerializerConfig.VALUE_SUBJECT_NAME_STRATEGY,
            KafkaStrategy.getStrategyName(avro_config.get("deserialization_strategy").asText()));



    // normal consumer
  //  properties.put("bootstrap.servers", "pkc-e8mp5.eu-west-1.aws.confluent.cloud:9092");
  //  properties.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
 //   properties.put("value.deserializer", "io.confluent.kafka.serializers.KafkaAvroDeserializer");


    //properties.put("auto.offset.reset", "earliest");

 //   properties.put("sasl.jaas.config", "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"KEPWQXZOVJFGKREP\" password=\"3NjIiv0BppSttm5RbVbIb2nx1Y8JWHpueq0g1+lTxvyPHpoWSXgujlkqDmxr3WqV\";");
  //  properties.put("security.protocol", "SASL_SSL");
  //  properties.put("sasl.mechanism", "PLAIN");
   // properties.put("ssl.endpoint.identification.algorithm", "https");
   // properties.put("auto.register.schemas", "true");
 //   properties.put("schema.registry.url", "https://psrc-8vyvr.eu-central-1.aws.confluent.cloud");
    Random random = new Random();
    // genera numero casuale tra 0 e 3
    int number = random.nextInt(50000);
    properties.put("group.id", "test-"+ number);
//    properties.put("schema.registry.basic.auth.credentials.source" ,  "USER_INFO");
//    properties.put("schema.registry.basic.auth.user.info" ,  "BDDHNB6IT6DRT4E4:vtKtc4k0xwdQ5xHEojKpaifNxjQopDEUAyJf9hy3bj+kv1B1ZnD+TzLgbztMLR1s");
    return properties;
  }

  @Override
  protected KafkaConsumer<String, GenericRecord> getConsumer() {
    if (consumer != null) {
      return consumer;
    }
    Map<String, Object> filteredProps = getKafkaConfig();
    consumer = new KafkaConsumer<>(filteredProps);

    final JsonNode subscription = config.get("subscription");
    LOGGER.info("Kafka subscribe method: {}", subscription.toString());
    switch (subscription.get("subscription_type").asText()) {
      case "subscribe" -> {
        final String topicPattern = subscription.get("topic_pattern").asText();
        consumer.subscribe(Pattern.compile(topicPattern));
        topicsToSubscribe = consumer.listTopics().keySet().stream()
            .filter(topic -> topic.matches(topicPattern))
            .collect(Collectors.toSet());
        LOGGER.info("Topic list: {}", topicsToSubscribe);
      }
      case "assign" -> {
        topicsToSubscribe = new HashSet<>();
        final String topicPartitions = subscription.get("topic_partitions").asText();
        final String[] topicPartitionsStr = topicPartitions.replaceAll("\\s+", "").split(",");
        final List<TopicPartition> topicPartitionList = Arrays.stream(topicPartitionsStr).map(topicPartition -> {
          final String[] pair = topicPartition.split(":");
          topicsToSubscribe.add(pair[0]);
          return new TopicPartition(pair[0], Integer.parseInt(pair[1]));
        }).collect(Collectors.toList());
        LOGGER.info("Topic-partition list: {}", topicPartitionList);
        consumer.assign(topicPartitionList);
      }
    }
    return consumer;
  }

  @Override
  protected Set<String> getTopicsToSubscribe() {
    if (topicsToSubscribe == null) {
      getConsumer();
    }
    return topicsToSubscribe;
  }

  @Override
  public boolean isAccessible() {
    try {
      final String testTopic = config.has("test_topic") ? config.get("test_topic").asText() : "";
      if (!testTopic.isBlank()) {
        final KafkaConsumer<String, GenericRecord> consumer = getConsumer();
        consumer.subscribe(Pattern.compile(testTopic));
        consumer.listTopics();
        consumer.close();
        LOGGER.info("Successfully connected to Kafka brokers for topic '{}'.", config.get("test_topic").asText());
      }
      return true;
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to connect to the Kafka brokers: ", e);
      return false;
    }
  }

  @Override
  public List<AirbyteStream> getStreams(final JsonNode config) {
    final JsonNode avroConfig = config.get("MessageFormat");
    String schemRegistryUrl = avroConfig.get("schema_registry_url").asText();

    Map<String, Object> properties = new HashMap<>();

    properties.put(SchemaRegistryClientConfig.BASIC_AUTH_CREDENTIALS_SOURCE, "USER_INFO");
    properties.put(SchemaRegistryClientConfig.USER_INFO_CONFIG, String.format("%s:%s", avroConfig.get("schema_registry_username").asText(), avroConfig.get("schema_registry_password").asText()));

    CachedSchemaRegistryClient schemaRegistryClient = new CachedSchemaRegistryClient(schemRegistryUrl, 1000, List.of(new AvroSchemaProvider()), properties);

    final Set<String> topicsToSubscribe = getTopicsToSubscribe();
    final List<AirbyteStream> streams = topicsToSubscribe.stream().map(topic ->
               CatalogHelpers
                      .createAirbyteStream(topic, Field.of("value", JsonSchemaType.STRING))
                       .withJsonSchema(extractSchemaStream(schemaRegistryClient, topic))
                      .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))

            )
        .collect(Collectors.toList());
    return streams;
  }

  private static JsonNode extractSchemaStream(CachedSchemaRegistryClient client, String topic) {
    try {
      SchemaMetadata schema = client.getLatestSchemaMetadata(topic+ "-value");
      Avro2JsonConvert converter = new  Avro2JsonConvert();
      return converter.convertoToAirbyteJson(schema.getSchema());
    } catch (Exception e) {
      LOGGER.error("Errore when extract and convert avro schema" + e.getMessage());
      throw new RuntimeException(e);
    }
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read() {

    final KafkaConsumer<String, GenericRecord> consumer = getConsumer();
    final List<ConsumerRecord<String, GenericRecord>> recordsList = new ArrayList<>();
    final int retry = config.has("repeated_calls") ? config.get("repeated_calls").intValue() : 0;
    final int polling_time = config.has("polling_time") ? config.get("polling_time").intValue() : 10000;
    final int max_records = config.has("max_records_process") ? config.get("max_records_process").intValue() : 100000;
    AtomicInteger record_count = new AtomicInteger();
    final Map<String, Integer> poll_lookup = new HashMap<>();
    getTopicsToSubscribe().forEach(topic -> poll_lookup.put(topic, 0));
    while (true) {
      final ConsumerRecords<String, GenericRecord> consumerRecords = consumer.poll(Duration.of(polling_time, ChronoUnit.MILLIS));
      consumerRecords.forEach(record -> {
        record_count.getAndIncrement();
        recordsList.add(record);
      });

      consumer.commitAsync();

      if (consumerRecords.count() == 0) {
        consumer.assignment().stream().map(record -> record.topic()).distinct().forEach(
            topic -> {
              poll_lookup.put(topic, poll_lookup.get(topic) + 1);
            });
        boolean is_complete = poll_lookup.entrySet().stream().allMatch(
            e -> e.getValue() > retry);
        if (is_complete) {
          LOGGER.info("There is no new data in the queue!!");
          break;
        }
      } else if (record_count.get() > max_records) {
        LOGGER.info("Max record count is reached !!");
        break;
      }
    }
    consumer.close();
    final Iterator<ConsumerRecord<String, GenericRecord>> iterator = recordsList.iterator();
    return AutoCloseableIterators.fromIterator(new AbstractIterator<>() {

      @Override
      protected AirbyteMessage computeNext() {
        if (iterator.hasNext()) {
          final ConsumerRecord<String, GenericRecord> record = iterator.next();
          GenericRecord avro_data = record.value();
          ObjectMapper mapper = new ObjectMapper();
          Schema schema = avro_data.getSchema();
          LOGGER.info("Schema avro"+ schema.toString());
          String namespace = avro_data.getSchema().getNamespace();
          String name = avro_data.getSchema().getName();
          JsonNode output;
          try {
            // Todo dynamic namespace is not supported now hence, adding avro schema name in the message
            if (StringUtils.isNoneEmpty(namespace) && StringUtils.isNoneEmpty(name)) {
              String newString = String.format("{\"avro_schema\": \"%s\",\"name\":\"%s\"}", namespace, name);
              JsonNode newNode = mapper.readTree(newString);
              output = mapper.readTree(avro_data.toString());
              ((ObjectNode) output).set("_namespace_", newNode);
            } else {
              output = mapper.readTree(avro_data.toString());
            }
          } catch (JsonProcessingException e) {
            LOGGER.error("Exception whilst reading avro data from stream", e);
            throw new RuntimeException(e);
          }
          return new AirbyteMessage()
              .withType(AirbyteMessage.Type.RECORD)
              .withRecord(new AirbyteRecordMessage()
                  .withStream(record.topic())
                  .withEmittedAt(Instant.now().toEpochMilli())
                  .withData(output));
        }

        return endOfData();
      }

    });
  }

}
