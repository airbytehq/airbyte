/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.format;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.CaseFormat;
import com.google.common.collect.AbstractIterator;
import com.google.common.collect.Lists;
import com.google.protobuf.Descriptors;
import com.google.protobuf.DynamicMessage;
import com.google.protobuf.util.JsonFormat;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.kafka.KafkaStrategy;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.SyncMode;
import io.confluent.kafka.schemaregistry.client.CachedSchemaRegistryClient;
import io.confluent.kafka.schemaregistry.client.SchemaMetadata;
import io.confluent.kafka.schemaregistry.client.SchemaRegistryClient;
import io.confluent.kafka.schemaregistry.client.SchemaRegistryClientConfig;
import io.confluent.kafka.schemaregistry.client.rest.exceptions.RestClientException;
import io.confluent.kafka.schemaregistry.protobuf.ProtobufSchema;
import io.confluent.kafka.serializers.protobuf.KafkaProtobufDeserializer;
import io.confluent.kafka.serializers.protobuf.KafkaProtobufDeserializerConfig;
import io.confluent.kafka.serializers.protobuf.KafkaProtobufSerializerConfig;

import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * ProtobufFormat handles Kafka message consumption and processing for Protobuf formatted data.
 * This class integrates with Confluent Schema Registry to deserialize Protobuf messages
 * and convert them to Airbyte messages.
 */
public class ProtobufFormat extends AbstractFormat {

  private static final Logger LOGGER = LoggerFactory.getLogger(ProtobufFormat.class);

  // Configuration constants
  private static final String MESSAGE_FORMAT_CONFIG_KEY = "MessageFormat";
  private static final String VALUE_SUBJECT_SUFFIX = "-value";
  private static final String SUBSCRIPTION_TYPE_SUBSCRIBE = "subscribe";
  private static final String SUBSCRIPTION_TYPE_ASSIGN = "assign";
  
  // Default configuration values
  private static final int DEFAULT_RETRY_COUNT = 0;
  private static final int DEFAULT_POLLING_TIME_MS = 100;
  private static final int DEFAULT_MAX_RECORDS = 100000;
  private static final int DEFAULT_SCHEMA_CACHE_SIZE = 1000;

  // Reusable instances for better performance
  private static final ObjectMapper JSON_MAPPER = new ObjectMapper();
  private static final JsonFormat.Printer PROTOBUF_JSON_PRINTER = JsonFormat.printer()
      .includingDefaultValueFields()
      .preservingProtoFieldNames();

  private KafkaConsumer<String, DynamicMessage> consumer;

  public ProtobufFormat(JsonNode jsonConfig) {
    super(jsonConfig);
  }

  /**
   * Configures Kafka consumer properties for Protobuf message deserialization.
   * Sets up Schema Registry authentication and deserialization strategy.
   *
   * @return Map of Kafka consumer configuration properties
   */
  @Override
  protected Map<String, Object> getKafkaConfig() {
    Map<String, Object> props = super.getKafkaConfig();
    final JsonNode protobufConfig = config.get(MESSAGE_FORMAT_CONFIG_KEY);
    
    // Configure deserializers
    props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
    props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, KafkaProtobufDeserializer.class.getName());
    
    // Configure Schema Registry authentication
    if (protobufConfig.has("schema_registry_username")) {
      props.put(SchemaRegistryClientConfig.BASIC_AUTH_CREDENTIALS_SOURCE, "USER_INFO");
      props.put(SchemaRegistryClientConfig.USER_INFO_CONFIG,
          String.format("%s:%s", 
              protobufConfig.get("schema_registry_username").asText(), 
              protobufConfig.get("schema_registry_password").asText()));
    } else {
      // If registry username is missing and SASL mechanism is OAUTHBEARER, use inherited credentials
      final JsonNode protocolConfig = config.get("protocol");
      if (protocolConfig.has("sasl_mechanism") &&
          protocolConfig.get("sasl_mechanism").asText().equals(OAuthBearerLoginModule.OAUTHBEARER_MECHANISM)) {
        props.put(SchemaRegistryClientConfig.BEARER_AUTH_CREDENTIALS_SOURCE, "SASL_OAUTHBEARER_INHERIT");
      }
    }
    
    // Configure Schema Registry URL and deserialization strategy
    props.put(KafkaProtobufDeserializerConfig.SCHEMA_REGISTRY_URL_CONFIG, 
        protobufConfig.get("schema_registry_url").asText());
    props.put(KafkaProtobufSerializerConfig.VALUE_SUBJECT_NAME_STRATEGY,
        KafkaStrategy.getStrategyName(protobufConfig.get("deserialization_strategy").asText()));
    
    return props;
  }

  /**
   * Creates and configures a Kafka consumer for Protobuf messages.
   * Handles both subscription patterns and topic-partition assignments.
   *
   * @return Configured KafkaConsumer instance
   */
  @Override
  protected KafkaConsumer<String, DynamicMessage> getConsumer() {
    if (consumer != null) {
      return consumer;
    }
    
    Map<String, Object> filteredProps = getKafkaConfig();
    consumer = new KafkaConsumer<>(filteredProps);

    final JsonNode subscription = config.get("subscription");
    LOGGER.info("Kafka subscribe method: {}", subscription.toString());
    
    switch (subscription.get("subscription_type").asText()) {
      case SUBSCRIPTION_TYPE_SUBSCRIBE -> {
        // Subscribe to topics matching a pattern
        final String topicPattern = subscription.get("topic_pattern").asText();
        consumer.subscribe(Pattern.compile(topicPattern));
        topicsToSubscribe = consumer.listTopics().keySet().stream()
            .filter(topic -> topic.matches(topicPattern))
            .collect(Collectors.toSet());
        LOGGER.info("Topic list: {}", topicsToSubscribe);
      }
      case SUBSCRIPTION_TYPE_ASSIGN -> {
        // Assign specific topic-partition combinations
        topicsToSubscribe = new HashSet<>();
        final String topicPartitions = subscription.get("topic_partitions").asText();
        final String[] topicPartitionsStr = topicPartitions.replaceAll("\\s+", "").split(",");
        final List<TopicPartition> topicPartitionList = Arrays.stream(topicPartitionsStr)
            .map(topicPartition -> {
              final String[] pair = topicPartition.split(":");
              topicsToSubscribe.add(pair[0]);
              return new TopicPartition(pair[0], Integer.parseInt(pair[1]));
            })
            .collect(Collectors.toList());
        LOGGER.info("Topic-partition list: {}", topicPartitionList);
        consumer.assign(topicPartitionList);
      }
    }
    
    return consumer;
  }

  /**
   * Gets the set of topics to subscribe to.
   * Initializes the consumer if not already done.
   *
   * @return Set of topic names
   */
  @Override
  protected Set<String> getTopicsToSubscribe() {
    if (topicsToSubscribe == null) {
      getConsumer();
    }
    return topicsToSubscribe;
  }

  /**
   * Tests connectivity to Kafka brokers by attempting to list topics.
   *
   * @return true if connection is successful, false otherwise
   */
  @Override
  public boolean isAccessible() {
    try {
      final String testTopic = config.has("test_topic") ? config.get("test_topic").asText() : "";
      if (!testTopic.isBlank()) {
        final KafkaConsumer<String, DynamicMessage> consumer = getConsumer();
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

  /**
   * Discovers available streams by querying Schema Registry for each topic
   * and building Airbyte stream definitions from Protobuf schemas.
   *
   * @return List of AirbyteStream objects representing available topics
   */
  @Override
  public List<AirbyteStream> getStreams() {
    final Set<String> topicsToSubscribe = getTopicsToSubscribe();
    return topicsToSubscribe.stream()
        .map(topic -> {
          try {
            Descriptors.Descriptor descriptor = buildDescriptorFromSchemaRegistry(topic + VALUE_SUBJECT_SUFFIX);
            return CatalogHelpers
                .createAirbyteStream(topic, buildFieldsFromDescriptor(descriptor).toArray(Field[]::new))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
          } catch (IOException | RestClientException e) {
            throw new RuntimeException(e);
          }
        })
        .toList();
  }

  /**
   * Builds Airbyte Field definitions from a Protobuf Descriptor.
   *
   * @param descriptor Protobuf message descriptor
   * @return List of Airbyte Field objects
   */
  private List<Field> buildFieldsFromDescriptor(Descriptors.Descriptor descriptor) {
    List<Field> fields = new ArrayList<>();
    
    for (Descriptors.FieldDescriptor fieldDescriptor : descriptor.getFields()) {
      String fieldName = fieldDescriptor.getName();
      JsonSchemaType fieldType = getJsonSchemaTypeFromProtobufField(fieldDescriptor);
      fields.add(Field.of(fieldName, fieldType));
    }

    return fields;
  }

  /**
   * Maps Protobuf field types to corresponding JSON Schema types.
   *
   * @param fieldDescriptor Protobuf field descriptor
   * @return Corresponding JsonSchemaType
   */
  private JsonSchemaType getJsonSchemaTypeFromProtobufField(Descriptors.FieldDescriptor fieldDescriptor) {
    return switch (fieldDescriptor.getType()) {
      case DOUBLE, FLOAT -> JsonSchemaType.NUMBER;
      case INT64, UINT64, INT32, FIXED64, FIXED32, UINT32, SFIXED32, SFIXED64, SINT32, SINT64 ->
          JsonSchemaType.INTEGER;
      case BOOL -> JsonSchemaType.BOOLEAN;
      case MESSAGE -> JsonSchemaType.OBJECT;
      default -> JsonSchemaType.STRING; // STRING, BYTES, ENUM and others
    };
  }

  /**
   * Fetches and builds a Protobuf Descriptor from Schema Registry for the given subject.
   *
   * @param subject Schema Registry subject name
   * @return Protobuf message descriptor
   * @throws IOException if I/O error occurs
   * @throws RestClientException if Schema Registry communication fails
   */
  private Descriptors.Descriptor buildDescriptorFromSchemaRegistry(String subject)
      throws IOException, RestClientException {

    try (SchemaRegistryClient schemaRegistryClient = new CachedSchemaRegistryClient(
        (String) getKafkaConfig().get(KafkaProtobufDeserializerConfig.SCHEMA_REGISTRY_URL_CONFIG),
        DEFAULT_SCHEMA_CACHE_SIZE, // max schemas to cache
        new HashMap<>())) {

      // Fetch schema from Schema Registry
      LOGGER.debug("Fetching schema for subject: {}", subject);
      SchemaMetadata schemaMetadata = schemaRegistryClient.getLatestSchemaMetadata(subject);

      // Parse the protobuf schema
      ProtobufSchema protobufSchema = new ProtobufSchema(schemaMetadata.getSchema());

      // Build descriptor from the protobuf schema
      Descriptors.Descriptor descriptor = protobufSchema.toDescriptor();

      // Validate that we have a valid descriptor
      if (descriptor == null) {
        throw new RuntimeException("Failed to build descriptor from protobuf schema");
      }

      return descriptor;
    } catch (Exception e) {
      LOGGER.error("Error building descriptor from Schema Registry: {}", e.getMessage());
      throw e;
    }
  }

  /**
   * Reads messages from Kafka topics and converts them to Airbyte messages.
   * Implements configurable polling with retry logic and record limits.
   *
   * @return AutoCloseableIterator of AirbyteMessage objects
   */
  @Override
  public AutoCloseableIterator<AirbyteMessage> read() {
    final KafkaConsumer<String, DynamicMessage> consumer = getConsumer();
    final List<ConsumerRecord<String, DynamicMessage>> recordsList = new ArrayList<>();
    
    // Configuration parameters
    final int retry = getRetryCount();
    final int pollingTime = getPollingTimeMs();
    final int maxRecords = getMaxRecords();
    
    AtomicInteger recordCount = new AtomicInteger();
    final Map<String, Integer> pollLookup = new HashMap<>();
    getTopicsToSubscribe().forEach(topic -> pollLookup.put(topic, 0));
    
    // Poll for messages until completion criteria are met
    while (true) {
      final ConsumerRecords<String, DynamicMessage> consumerRecords = 
          consumer.poll(Duration.of(pollingTime, ChronoUnit.MILLIS));
      
      consumerRecords.forEach(record -> {
        recordCount.getAndIncrement();
        recordsList.add(record);
      });
      
      consumer.commitAsync();

      if (consumerRecords.count() == 0) {
        // Track empty polls per topic
        consumer.assignment().stream()
            .map(TopicPartition::topic)
            .distinct()
            .forEach(topic -> pollLookup.put(topic, pollLookup.get(topic) + 1));
        
        // Check if all topics have exceeded retry limit
        boolean isComplete = pollLookup.entrySet().stream()
            .allMatch(entry -> entry.getValue() > retry);
        
        if (isComplete) {
          LOGGER.info("No new data in the queue - polling complete");
          break;
        }
      } else if (recordCount.get() > maxRecords) {
        LOGGER.info("Max record count reached: {}", recordCount.get());
        break;
      }
    }
    
    consumer.close();
    final Iterator<ConsumerRecord<String, DynamicMessage>> iterator = recordsList.iterator();
    
    return AutoCloseableIterators.fromIterator(new AbstractIterator<>() {
      @Override
      protected AirbyteMessage computeNext() {
        if (iterator.hasNext()) {
          final ConsumerRecord<String, DynamicMessage> record = iterator.next();
          return convertRecordToAirbyteMessage(record);
        }
        return endOfData();
      }
    });
  }

  /**
   * Gets the retry count from configuration with default fallback.
   *
   * @return retry count
   */
  private int getRetryCount() {
    return config.has("repeated_calls") ? config.get("repeated_calls").intValue() : DEFAULT_RETRY_COUNT;
  }

  /**
   * Gets the polling time in milliseconds from configuration with default fallback.
   *
   * @return polling time in milliseconds
   */
  private int getPollingTimeMs() {
    return config.has("polling_time") ? config.get("polling_time").intValue() : DEFAULT_POLLING_TIME_MS;
  }

  /**
   * Gets the maximum records to process from configuration with default fallback.
   *
   * @return maximum records count
   */
  private int getMaxRecords() {
    return config.has("max_records_process") ? config.get("max_records_process").intValue() : DEFAULT_MAX_RECORDS;
  }

  /**
   * Converts a Kafka ConsumerRecord to an AirbyteMessage.
   * Handles Protobuf to JSON conversion and error handling.
   *
   * @param record Kafka consumer record containing DynamicMessage
   * @return AirbyteMessage with converted data
   * @throws RuntimeException if conversion fails
   */
  private AirbyteMessage convertRecordToAirbyteMessage(ConsumerRecord<String, DynamicMessage> record) {
    if (record == null) {
      throw new IllegalArgumentException("Consumer record cannot be null");
    }
    
    DynamicMessage protobufData = record.value();
    if (protobufData == null) {
      LOGGER.warn("Received null protobuf data for topic: {}, partition: {}, offset: {}", 
          record.topic(), record.partition(), record.offset());
      // Return empty JSON object for null values
      return createAirbyteMessage(record.topic(), JSON_MAPPER.createObjectNode());
    }
    
    JsonNode output;
    try {
      // Convert Protobuf message to JSON
      String jsonString = PROTOBUF_JSON_PRINTER.print(protobufData);
      output = JSON_MAPPER.readTree(jsonString);
    } catch (Exception e) {
      LOGGER.error("Failed to convert protobuf message to JSON for topic: {}, partition: {}, offset: {}", 
          record.topic(), record.partition(), record.offset(), e);
      throw new RuntimeException("Protobuf to JSON conversion failed", e);
    }
    
    LOGGER.debug("Successfully processed record from topic: {}", record.topic());
    return createAirbyteMessage(record.topic(), output);
  }

  /**
   * Creates an AirbyteMessage with the given stream name and data.
   *
   * @param streamName the name of the stream
   * @param data the JSON data
   * @return AirbyteMessage instance
   */
  private AirbyteMessage createAirbyteMessage(String streamName, JsonNode data) {
    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withEmittedAt(Instant.now().toEpochMilli())
            .withData(data));
  }
}
