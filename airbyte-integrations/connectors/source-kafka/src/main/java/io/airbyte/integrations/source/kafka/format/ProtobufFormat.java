/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.format;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.AbstractIterator;
import com.google.common.collect.Lists;
import com.google.protobuf.Descriptors;
import com.google.protobuf.DynamicMessage;
import com.google.protobuf.InvalidProtocolBufferException;
import com.google.protobuf.util.JsonFormat;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
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
import io.confluent.kafka.schemaregistry.client.rest.exceptions.RestClientException;
import io.confluent.kafka.schemaregistry.protobuf.ProtobufSchema;

import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Function;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.errors.WakeupException;
import org.apache.kafka.common.serialization.ByteArrayDeserializer;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * ProtobufFormat handles Kafka message consumption and processing for Protobuf formatted data.
 * This class integrates with Confluent Schema Registry to deserialize Protobuf messages
 * and convert them to Airbyte messages.
 * 
 * <p>Key features:
 * <ul>
 *   <li>Schema Registry integration for dynamic Protobuf schema resolution</li>
 *   <li>Configurable polling with retry logic and record limits</li>
 *   <li>Support for both topic subscription patterns and partition assignments</li>
 *   <li>Thread-safe descriptor caching for improved performance</li>
 *   <li>Comprehensive error handling and resource management</li>
 * </ul>
 */
public class ProtobufFormat extends AbstractFormat {

  private static final Logger LOGGER = LoggerFactory.getLogger(ProtobufFormat.class);

  // Configuration constants
  private static final String MESSAGE_FORMAT_CONFIG_KEY = "MessageFormat";
  private static final String SCHEMA_REGISTRY_URL_KEY = "schema_registry_url";
  private static final String VALUE_SUBJECT_SUFFIX = "-value";
  private static final String SUBSCRIPTION_TYPE_SUBSCRIBE = "subscribe";
  private static final String SUBSCRIPTION_TYPE_ASSIGN = "assign";
  
  // Configuration field names
  private static final String SUBSCRIPTION_FIELD = "subscription";
  private static final String SUBSCRIPTION_TYPE_FIELD = "subscription_type";
  private static final String TOPIC_PATTERN_FIELD = "topic_pattern";
  private static final String TOPIC_PARTITIONS_FIELD = "topic_partitions";
  private static final String TEST_TOPIC_FIELD = "test_topic";
  private static final String REPEATED_CALLS_FIELD = "repeated_calls";
  private static final String POLLING_TIME_FIELD = "polling_time";
  private static final String MAX_RECORDS_PROCESS_FIELD = "max_records_process";

  // Default configuration values
  private static final int DEFAULT_RETRY_COUNT = 0;
  private static final int DEFAULT_POLLING_TIME_MS = 100;
  private static final int DEFAULT_MAX_RECORDS = 100_000;
  private static final int DEFAULT_SCHEMA_CACHE_SIZE = 1000;
  private static final int CONFLUENT_MAGIC_BYTE_LENGTH = 5;
  private static final byte CONFLUENT_MAGIC_BYTE = 0;

  // Reusable instances for better performance
  private static final ObjectMapper JSON_MAPPER = new ObjectMapper();
  private static final JsonFormat.Printer PROTOBUF_JSON_PRINTER = JsonFormat.printer()
      .includingDefaultValueFields()
      .preservingProtoFieldNames();

  // Thread-safe cache for descriptors
  private final Map<String, Descriptors.Descriptor> descriptorCache = new ConcurrentHashMap<>();
  
  // Consumer instance - using volatile for thread safety
  private volatile KafkaConsumer<String, byte[]> consumer;

  /**
   * Constructs a new ProtobufFormat instance with the provided configuration.
   *
   * @param jsonConfig the JSON configuration containing connection and format settings
   * @throws IllegalArgumentException if the configuration is null or invalid
   */
  public ProtobufFormat(final JsonNode jsonConfig) {
    super(jsonConfig);
  }


  /**
   * Configures Kafka consumer properties for Protobuf message deserialization.
   * Sets up deserializers for string keys and byte array values.
   *
   * @return Map of Kafka consumer configuration properties
   */
  @Override
  protected Map<String, Object> getKafkaConfig() {
    final Map<String, Object> props = super.getKafkaConfig();

    // Configure deserializers for Protobuf format
    props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
    props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, ByteArrayDeserializer.class.getName());

    return props;
  }

  /**
   * Creates and configures a Kafka consumer for Protobuf messages.
   * Handles both subscription patterns and topic-partition assignments.
   * Uses double-checked locking pattern for thread-safe lazy initialization.
   *
   * @return Configured KafkaConsumer instance
   * @throws IllegalStateException if consumer configuration fails
   */
  @Override
  protected KafkaConsumer<String, byte[]> getConsumer() {
    if (consumer != null) {
      return consumer;
    }
    
    synchronized (this) {
      if (consumer != null) {
        return consumer;
      }
      
      try {
        final Map<String, Object> kafkaConfig = getKafkaConfig();
        consumer = new KafkaConsumer<>(kafkaConfig);
        configureConsumerSubscription();
        
        LOGGER.info("Successfully created Kafka consumer with topics: {}", topicsToSubscribe);
        return consumer;
      } catch (final Exception e) {
        LOGGER.error("Failed to create Kafka consumer", e);
        throw new IllegalStateException("Unable to create Kafka consumer", e);
      }
    }
  }

  /**
   * Configures the consumer subscription based on the configuration.
   * Supports both pattern-based subscription and explicit partition assignment.
   */
  private void configureConsumerSubscription() {
    final JsonNode subscription = config.get(SUBSCRIPTION_FIELD);
    final String subscriptionType = subscription.get(SUBSCRIPTION_TYPE_FIELD).asText();
    
    LOGGER.info("Configuring Kafka subscription with type: {}", subscriptionType);
    
    switch (subscriptionType) {
      case SUBSCRIPTION_TYPE_SUBSCRIBE -> configurePatternSubscription(subscription);
      case SUBSCRIPTION_TYPE_ASSIGN -> configurePartitionAssignment(subscription);
      default -> throw new IllegalArgumentException("Unsupported subscription type: " + subscriptionType);
    }
  }

  /**
   * Configures pattern-based topic subscription.
   *
   * @param subscription the subscription configuration
   */
  private void configurePatternSubscription(final JsonNode subscription) {
    if (!subscription.has(TOPIC_PATTERN_FIELD)) {
      throw new IllegalArgumentException("Missing required field for subscribe: " + TOPIC_PATTERN_FIELD);
    }
    
    final String topicPattern = subscription.get(TOPIC_PATTERN_FIELD).asText();
    if (topicPattern == null || topicPattern.trim().isEmpty()) {
      throw new IllegalArgumentException("Topic pattern cannot be empty");
    }
    
    try {
      final Pattern pattern = Pattern.compile(topicPattern);
      consumer.subscribe(pattern);
      
      // Get matching topics
      topicsToSubscribe = consumer.listTopics().keySet().stream()
          .filter(topic -> pattern.matcher(topic).matches())
          .collect(Collectors.toSet());
          
      LOGGER.info("Subscribed to pattern '{}' matching topics: {}", topicPattern, topicsToSubscribe);
    } catch (final Exception e) {
      throw new IllegalArgumentException("Invalid topic pattern: " + topicPattern, e);
    }
  }

  /**
   * Configures explicit partition assignment.
   *
   * @param subscription the subscription configuration
   */
  private void configurePartitionAssignment(final JsonNode subscription) {
    if (!subscription.has(TOPIC_PARTITIONS_FIELD)) {
      throw new IllegalArgumentException("Missing required field for assign: " + TOPIC_PARTITIONS_FIELD);
    }
    
    final String topicPartitions = subscription.get(TOPIC_PARTITIONS_FIELD).asText();
    if (topicPartitions == null || topicPartitions.trim().isEmpty()) {
      throw new IllegalArgumentException("Topic partitions cannot be empty");
    }
    
    topicsToSubscribe = new HashSet<>();
    
    try {
      final String[] topicPartitionsArray = topicPartitions.replaceAll("\\s+", "").split(",");
      final List<TopicPartition> topicPartitionList = Arrays.stream(topicPartitionsArray)
          .filter(tp -> !tp.trim().isEmpty())
          .map(this::parseTopicPartition)
          .collect(Collectors.toList());
          
      consumer.assign(topicPartitionList);
      LOGGER.info("Assigned to topic-partitions: {}", topicPartitionList);
    } catch (final Exception e) {
      throw new IllegalArgumentException("Invalid topic partitions format: " + topicPartitions, e);
    }
  }

  /**
   * Parses a topic:partition string into a TopicPartition object.
   *
   * @param topicPartition the topic:partition string
   * @return TopicPartition object
   * @throws IllegalArgumentException if the format is invalid
   */
  private TopicPartition parseTopicPartition(final String topicPartition) {
    final String[] parts = topicPartition.split(":");
    if (parts.length != 2) {
      throw new IllegalArgumentException("Invalid topic:partition format: " + topicPartition);
    }
    
    final String topic = parts[0].trim();
    if (topic.isEmpty()) {
      throw new IllegalArgumentException("Topic name cannot be empty in: " + topicPartition);
    }
    
    try {
      final int partition = Integer.parseInt(parts[1].trim());
      if (partition < 0) {
        throw new IllegalArgumentException("Partition number cannot be negative: " + partition);
      }
      
      topicsToSubscribe.add(topic);
      return new TopicPartition(topic, partition);
    } catch (final NumberFormatException e) {
      throw new IllegalArgumentException("Invalid partition number in: " + topicPartition, e);
    }
  }

  /**
   * Gets the set of topics to subscribe to.
   * Initializes the consumer if not already done.
   *
   * @return Set of topic names (never null, may be empty)
   */
  @Override
  protected Set<String> getTopicsToSubscribe() {
    if (topicsToSubscribe == null) {
      getConsumer();
    }
    return topicsToSubscribe != null ? topicsToSubscribe : Collections.emptySet();
  }

  /**
   * Tests connectivity to Kafka brokers and Schema Registry.
   * Performs basic connectivity checks without consuming messages.
   *
   * @return true if connection is successful, false otherwise
   */
  @Override
  public boolean isAccessible() {
    KafkaConsumer<String, byte[]> testConsumer = null;
    
    try {
      // Test Kafka connectivity
      final String testTopic = config.has(TEST_TOPIC_FIELD) ? config.get(TEST_TOPIC_FIELD).asText() : "";
      
      if (!testTopic.trim().isEmpty()) {
        testConsumer = new KafkaConsumer<>(getKafkaConfig());
        testConsumer.subscribe(Pattern.compile(Pattern.quote(testTopic)));
        
        // This will trigger metadata fetch and validate connectivity
        testConsumer.listTopics(Duration.ofSeconds(10));
        
        LOGGER.info("Successfully connected to Kafka brokers for topic '{}'", testTopic);
      }
      
      // Test Schema Registry connectivity if configured
      if (isSchemaRegistryConfigured()) {
        testSchemaRegistryConnectivity();
      }
      
      return true;
    } catch (final Exception e) {
      LOGGER.error("Failed to connect to Kafka brokers or Schema Registry", e);
      return false;
    } finally {
      if (testConsumer != null) {
        try {
          testConsumer.close(Duration.ofSeconds(5));
        } catch (final Exception e) {
          LOGGER.warn("Failed to close test consumer", e);
        }
      }
    }
  }

  /**
   * Checks if Schema Registry is configured.
   *
   * @return true if Schema Registry URL is configured
   */
  private boolean isSchemaRegistryConfigured() {
    return config.has(MESSAGE_FORMAT_CONFIG_KEY) && 
           config.get(MESSAGE_FORMAT_CONFIG_KEY).has(SCHEMA_REGISTRY_URL_KEY);
  }

  /**
   * Tests Schema Registry connectivity.
   *
   * @throws Exception if connectivity test fails
   */
  private void testSchemaRegistryConnectivity() throws Exception {
    final String schemaRegistryUrl = config.get(MESSAGE_FORMAT_CONFIG_KEY)
        .get(SCHEMA_REGISTRY_URL_KEY).asText();
        
    try (final SchemaRegistryClient client = new CachedSchemaRegistryClient(
        schemaRegistryUrl, DEFAULT_SCHEMA_CACHE_SIZE, new HashMap<>())) {
      
      // Simple connectivity test
      client.getAllSubjects();
      LOGGER.info("Successfully connected to Schema Registry at: {}", schemaRegistryUrl);
    }
  }

  /**
   * Discovers available streams by querying Schema Registry for each topic
   * and building Airbyte stream definitions from Protobuf schemas.
   *
   * @return List of AirbyteStream objects representing available topics
   * @throws RuntimeException if stream discovery fails
   */
  @Override
  public List<AirbyteStream> getStreams() {
    final Set<String> topics = getTopicsToSubscribe();
    if (topics.isEmpty()) {
      LOGGER.warn("No topics found for stream discovery");
      return Collections.emptyList();
    }
    
    return topics.stream()
        .map(this::createStreamForTopic)
        .filter(Objects::nonNull)
        .collect(Collectors.toList());
  }

  /**
   * Creates an AirbyteStream for a given topic.
   *
   * @param topic the topic name
   * @return AirbyteStream or null if creation fails
   */
  private AirbyteStream createStreamForTopic(final String topic) {
    try {
      final Descriptors.Descriptor descriptor = getDescriptorForTopic(topic);
      final List<Field> fields = buildFieldsFromDescriptor(descriptor);
      
      return CatalogHelpers
          .createAirbyteStream(topic, fields.toArray(Field[]::new))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    } catch (final Exception e) {
      LOGGER.error("Failed to create stream for topic: {}", topic, e);
      return null;
    }
  }

  /**
   * Builds Airbyte Field definitions from a Protobuf Descriptor.
   * Recursively handles nested message types.
   *
   * @param descriptor Protobuf message descriptor
   * @return List of Airbyte Field objects (never null)
   */
  private List<Field> buildFieldsFromDescriptor(final Descriptors.Descriptor descriptor) {
    if (descriptor == null) {
      return Collections.emptyList();
    }
    
    final List<Field> fields = new ArrayList<>();
    
    for (final Descriptors.FieldDescriptor fieldDescriptor : descriptor.getFields()) {
      try {
        final String fieldName = fieldDescriptor.getName();
        final JsonSchemaType fieldType = mapProtobufTypeToJsonSchema(fieldDescriptor);
        fields.add(Field.of(fieldName, fieldType));
      } catch (final Exception e) {
        LOGGER.warn("Failed to process field: {}", fieldDescriptor.getName(), e);
      }
    }

    return fields;
  }

  /**
   * Maps Protobuf field types to corresponding JSON Schema types.
   * Handles all Protobuf types including repeated fields and nested messages.
   *
   * @param fieldDescriptor Protobuf field descriptor
   * @return Corresponding JsonSchemaType
   */
  private JsonSchemaType mapProtobufTypeToJsonSchema(final Descriptors.FieldDescriptor fieldDescriptor) {
    // Handle repeated fields as arrays
    if (fieldDescriptor.isRepeated()) {
      return JsonSchemaType.ARRAY;
    }
    
    return switch (fieldDescriptor.getType()) {
      case DOUBLE, FLOAT -> JsonSchemaType.NUMBER;
      case INT64, UINT64, INT32, FIXED64, FIXED32, UINT32, SFIXED32, SFIXED64, SINT32, SINT64 ->
          JsonSchemaType.INTEGER;
      case BOOL -> JsonSchemaType.BOOLEAN;
      case MESSAGE -> JsonSchemaType.OBJECT;
      case ENUM -> JsonSchemaType.STRING; // Enums are serialized as strings
      default -> JsonSchemaType.STRING; // STRING, BYTES, and others
    };
  }

  /**
   * Gets or creates a descriptor for the given topic.
   * Uses thread-safe caching to improve performance.
   *
   * @param topic the topic name
   * @return Protobuf message descriptor
   * @throws RuntimeException if descriptor creation fails
   */
  private Descriptors.Descriptor getDescriptorForTopic(final String topic) {
    return descriptorCache.computeIfAbsent(topic, this::buildDescriptorForTopic);
  }

  /**
   * Fetches and builds a Protobuf Descriptor from Schema Registry for the given topic.
   * Implements proper resource management and error handling.
   *
   * @param topic the topic name
   * @return Protobuf message descriptor
   * @throws RuntimeException if descriptor building fails
   */
  private Descriptors.Descriptor buildDescriptorForTopic(final String topic) {
    if (topic == null || topic.trim().isEmpty()) {
      throw new IllegalArgumentException("Topic name cannot be null or empty");
    }
    
    if (!isSchemaRegistryConfigured()) {
      throw new IllegalStateException("Schema Registry not configured");
    }
    
    final String subject = topic + VALUE_SUBJECT_SUFFIX;
    final String schemaRegistryUrl = config.get(MESSAGE_FORMAT_CONFIG_KEY)
        .get(SCHEMA_REGISTRY_URL_KEY).asText();

    try (final SchemaRegistryClient schemaRegistryClient = new CachedSchemaRegistryClient(
        schemaRegistryUrl, DEFAULT_SCHEMA_CACHE_SIZE, new HashMap<>())) {

      LOGGER.debug("Fetching schema for subject: {}", subject);
      
      final SchemaMetadata schemaMetadata = schemaRegistryClient.getLatestSchemaMetadata(subject);
      if (schemaMetadata == null) {
        throw new RuntimeException("No schema metadata found for subject: " + subject);
      }

      final ProtobufSchema protobufSchema = new ProtobufSchema(schemaMetadata.getSchema());
      final Descriptors.Descriptor descriptor = protobufSchema.toDescriptor();

      if (descriptor == null) {
        throw new RuntimeException("Failed to build descriptor from protobuf schema for subject: " + subject);
      }

      LOGGER.debug("Successfully built descriptor for subject: {}", subject);
      return descriptor;
    } catch (final RestClientException e) {
      LOGGER.error("Schema Registry error for subject {}: {}", subject, e.getMessage());
      throw new RuntimeException("Schema Registry error for subject " + subject, e);
    } catch (final IOException e) {
      LOGGER.error("I/O error while accessing Schema Registry for subject {}: {}", subject, e.getMessage());
      throw new RuntimeException("I/O error accessing Schema Registry for subject " + subject, e);
    } catch (final Exception e) {
      LOGGER.error("Unexpected error building descriptor for subject {}: {}", subject, e.getMessage());
      throw new RuntimeException("Failed to build descriptor for subject " + subject, e);
    }
  }

  /**
   * Reads messages from Kafka topics and converts them to Airbyte messages.
   * Implements configurable polling with retry logic and record limits.
   * Ensures proper resource cleanup even in case of exceptions.
   *
   * @return AutoCloseableIterator of AirbyteMessage objects
   * @throws RuntimeException if reading fails
   */
  @Override
  public AutoCloseableIterator<AirbyteMessage> read() {
    final KafkaConsumer<String, byte[]> kafkaConsumer = getConsumer();
    final List<ConsumerRecord<String, byte[]>> recordsList = new ArrayList<>();
    
    try {
      final RecordCollector collector = new RecordCollector(kafkaConsumer, getConfiguration());
      recordsList.addAll(collector.collectRecords());
    } catch (final Exception e) {
      LOGGER.error("Failed to collect records from Kafka", e);
      closeConsumerSafely();
      throw new RuntimeException("Failed to read from Kafka", e);
    }
    
    closeConsumerSafely();
    LOGGER.info("Collected {} records for processing", recordsList.size());
    
    return createMessageIterator(recordsList);
  }

  /**
   * Creates an iterator for converting records to Airbyte messages.
   *
   * @param recordsList the list of consumer records
   * @return AutoCloseableIterator of AirbyteMessage objects
   */
  private AutoCloseableIterator<AirbyteMessage> createMessageIterator(
      final List<ConsumerRecord<String, byte[]>> recordsList) {
    
    final Iterator<ConsumerRecord<String, byte[]>> iterator = recordsList.iterator();

    return AutoCloseableIterators.fromIterator(new AbstractIterator<AirbyteMessage>() {
      @Override
      protected AirbyteMessage computeNext() {
        if (iterator.hasNext()) {
          final ConsumerRecord<String, byte[]> record = iterator.next();
          try {
            return convertRecordToAirbyteMessage(record, getDescriptorForTopic(record.topic()));
          } catch (final Exception e) {
            LOGGER.error("Failed to convert record from topic: {}, partition: {}, offset: {}", 
                record.topic(), record.partition(), record.offset(), e);
            // Skip problematic records rather than failing completely
            return computeNext();
          }
        }
        return endOfData();
      }
    });
  }

  /**
   * Safely closes the Kafka consumer with proper error handling.
   */
  private void closeConsumerSafely() {
    if (consumer != null) {
      try {
        consumer.close(Duration.ofSeconds(10));
        LOGGER.debug("Successfully closed Kafka consumer");
      } catch (final Exception e) {
        LOGGER.warn("Failed to close Kafka consumer gracefully", e);
      } finally {
        consumer = null;
      }
    }
  }

  /**
   * Gets the current configuration for record collection.
   *
   * @return Configuration object
   */
  private RecordCollectionConfig getConfiguration() {
    return new RecordCollectionConfig(
        getRetryCount(),
        getPollingTimeMs(),
        getMaxRecords(),
        getTopicsToSubscribe()
    );
  }

  /**
   * Gets the retry count from configuration with default fallback.
   *
   * @return retry count (non-negative)
   */
  private int getRetryCount() {
    if (!config.has(REPEATED_CALLS_FIELD)) {
      return DEFAULT_RETRY_COUNT;
    }
    
    final int retryCount = config.get(REPEATED_CALLS_FIELD).asInt(DEFAULT_RETRY_COUNT);
    return Math.max(0, retryCount);
  }

  /**
   * Gets the polling time in milliseconds from configuration with default fallback.
   *
   * @return polling time in milliseconds (positive)
   */
  private int getPollingTimeMs() {
    if (!config.has(POLLING_TIME_FIELD)) {
      return DEFAULT_POLLING_TIME_MS;
    }
    
    final int pollingTime = config.get(POLLING_TIME_FIELD).asInt(DEFAULT_POLLING_TIME_MS);
    return Math.max(1, pollingTime);
  }

  /**
   * Gets the maximum records to process from configuration with default fallback.
   *
   * @return maximum records count (positive)
   */
  private int getMaxRecords() {
    if (!config.has(MAX_RECORDS_PROCESS_FIELD)) {
      return DEFAULT_MAX_RECORDS;
    }
    
    final int maxRecords = config.get(MAX_RECORDS_PROCESS_FIELD).asInt(DEFAULT_MAX_RECORDS);
    return Math.max(1, maxRecords);
  }

  /**
   * Parses a Protobuf message from raw bytes, handling Confluent Schema Registry format.
   * Supports both Confluent wire format (with magic byte and schema ID) and raw Protobuf.
   *
   * @param messageBytes the raw message bytes
   * @param descriptor the Protobuf message descriptor
   * @return parsed DynamicMessage
   * @throws InvalidProtocolBufferException if parsing fails
   */
  private DynamicMessage parseProtobufMessage(final byte[] messageBytes, 
                                              final Descriptors.Descriptor descriptor)
      throws InvalidProtocolBufferException {
    
    if (messageBytes == null || messageBytes.length == 0) {
      throw new InvalidProtocolBufferException("Message bytes cannot be null or empty");
    }
    
    final byte[] protobufBytes = extractProtobufBytes(messageBytes);
    return DynamicMessage.parseFrom(descriptor, protobufBytes);
  }

  /**
   * Extracts Protobuf bytes from message, handling Confluent wire format.
   *
   * @param messageBytes the raw message bytes
   * @return the Protobuf bytes
   */
  private byte[] extractProtobufBytes(final byte[] messageBytes) {
    // Check for Confluent Schema Registry wire format
    if (isConfluentWireFormat(messageBytes)) {
      // Skip magic byte (1 byte) + schema ID (4 bytes)
      final byte[] protobufBytes = new byte[messageBytes.length - CONFLUENT_MAGIC_BYTE_LENGTH];
      System.arraycopy(messageBytes, CONFLUENT_MAGIC_BYTE_LENGTH, protobufBytes, 0, protobufBytes.length);
      LOGGER.debug("Detected Confluent wire format, extracted {} bytes", protobufBytes.length);
      return protobufBytes;
    } else {
      // Raw Protobuf format
      LOGGER.debug("Detected raw Protobuf format");
      return messageBytes;
    }
  }

  /**
   * Checks if the message bytes follow Confluent Schema Registry wire format.
   *
   * @param messageBytes the message bytes
   * @return true if Confluent wire format is detected
   */
  private boolean isConfluentWireFormat(final byte[] messageBytes) {
    return messageBytes.length > CONFLUENT_MAGIC_BYTE_LENGTH && 
           messageBytes[0] == CONFLUENT_MAGIC_BYTE;
  }

  /**
   * Converts a Kafka ConsumerRecord to an AirbyteMessage.
   * Handles Protobuf to JSON conversion with comprehensive error handling.
   *
   * @param record Kafka consumer record containing raw bytes
   * @param descriptor Protobuf message descriptor
   * @return AirbyteMessage with converted data
   * @throws IllegalArgumentException if record is null
   * @throws RuntimeException if conversion fails critically
   */
  private AirbyteMessage convertRecordToAirbyteMessage(
      final ConsumerRecord<String, byte[]> record,
      final Descriptors.Descriptor descriptor) {
    
    if (record == null) {
      throw new IllegalArgumentException("Consumer record cannot be null");
    }

    final byte[] dataBytes = record.value();
    if (dataBytes == null || dataBytes.length == 0) {
      LOGGER.warn("Received null or empty data for topic: {}, partition: {}, offset: {}",
          record.topic(), record.partition(), record.offset());
      return createAirbyteMessage(record.topic(), JSON_MAPPER.createObjectNode());
    }

    try {
      final DynamicMessage protobufData = parseProtobufMessage(dataBytes, descriptor);
      final String jsonString = PROTOBUF_JSON_PRINTER.print(protobufData);
      final JsonNode output = JSON_MAPPER.readTree(jsonString);
      
      LOGGER.debug("Successfully processed record from topic: {}, size: {} bytes", 
          record.topic(), dataBytes.length);
      return createAirbyteMessage(record.topic(), output);
      
    } catch (final InvalidProtocolBufferException e) {
      LOGGER.error("Invalid Protobuf data for topic: {}, partition: {}, offset: {}", 
          record.topic(), record.partition(), record.offset(), e);
      throw new RuntimeException("Invalid Protobuf data", e);
    } catch (final Exception e) {
      LOGGER.error("Failed to convert protobuf message to JSON for topic: {}, partition: {}, offset: {}", 
          record.topic(), record.partition(), record.offset(), e);
      throw new RuntimeException("Protobuf to JSON conversion failed", e);
    }
  }

  /**
   * Creates an AirbyteMessage with the given stream name and data.
   *
   * @param streamName the name of the stream (must not be null)
   * @param data the JSON data (must not be null)
   * @return AirbyteMessage instance
   * @throws IllegalArgumentException if parameters are null
   */
  private AirbyteMessage createAirbyteMessage(final String streamName, final JsonNode data) {
    if (streamName == null) {
      throw new IllegalArgumentException("Stream name cannot be null");
    }
    if (data == null) {
      throw new IllegalArgumentException("Data cannot be null");
    }
    
    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withEmittedAt(Instant.now().toEpochMilli())
            .withData(data));
  }

  /**
   * Configuration class for record collection parameters.
   */
  private static class RecordCollectionConfig {
    private final int retryCount;
    private final int pollingTimeMs;
    private final int maxRecords;
    private final Set<String> topics;

    public RecordCollectionConfig(final int retryCount, final int pollingTimeMs, 
                                  final int maxRecords, final Set<String> topics) {
      this.retryCount = retryCount;
      this.pollingTimeMs = pollingTimeMs;
      this.maxRecords = maxRecords;
      this.topics = topics != null ? new HashSet<>(topics) : Collections.emptySet();
    }

    public int getRetryCount() { return retryCount; }
    public int getPollingTimeMs() { return pollingTimeMs; }
    public int getMaxRecords() { return maxRecords; }
    public Set<String> getTopics() { return topics; }
  }

  /**
   * Helper class for collecting records from Kafka with proper polling logic.
   */
  private static class RecordCollector {
    private static final Logger LOGGER = LoggerFactory.getLogger(RecordCollector.class);
    
    private final KafkaConsumer<String, byte[]> consumer;
    private final RecordCollectionConfig config;
    private final AtomicInteger recordCount = new AtomicInteger(0);
    private final Map<String, Integer> pollRetryLookup = new HashMap<>();

    public RecordCollector(final KafkaConsumer<String, byte[]> consumer, 
                          final RecordCollectionConfig config) {
      this.consumer = Objects.requireNonNull(consumer, "Consumer cannot be null");
      this.config = Objects.requireNonNull(config, "Config cannot be null");
      
      // Initialize retry tracking for each topic
      config.getTopics().forEach(topic -> pollRetryLookup.put(topic, 0));
    }

    /**
     * Collects records from Kafka with retry logic and limits.
     *
     * @return List of collected records
     * @throws RuntimeException if collection fails
     */
    public List<ConsumerRecord<String, byte[]>> collectRecords() {
      final List<ConsumerRecord<String, byte[]>> recordsList = new ArrayList<>();
      
      try {
        while (shouldContinuePolling()) {
          final ConsumerRecords<String, byte[]> consumerRecords = pollForRecords();
          
          if (consumerRecords.isEmpty()) {
            handleEmptyPoll();
          } else {
            processRecords(consumerRecords, recordsList);
            resetRetryCounters();
          }
          
          commitOffsetsAsync();
          
          if (recordCount.get() >= config.getMaxRecords()) {
            LOGGER.info("Reached maximum record limit: {}", recordCount.get());
            break;
          }
        }
      } catch (final WakeupException e) {
        LOGGER.info("Consumer was woken up during polling");
        throw new RuntimeException("Consumer interrupted", e);
      } catch (final Exception e) {
        LOGGER.error("Error during record collection", e);
        throw new RuntimeException("Failed to collect records", e);
      }
      
      LOGGER.info("Collected {} records from {} topics", recordCount.get(), config.getTopics().size());
      return recordsList;
    }

    private boolean shouldContinuePolling() {
      if (recordCount.get() >= config.getMaxRecords()) {
        return false;
      }
      
      // Check if all topics have exceeded retry limit
      return !pollRetryLookup.values().stream().allMatch(count -> count > config.getRetryCount());
    }

    private ConsumerRecords<String, byte[]> pollForRecords() {
      final Duration pollTimeout = Duration.of(config.getPollingTimeMs(), ChronoUnit.MILLIS);
      return consumer.poll(pollTimeout);
    }

    private void handleEmptyPoll() {
      // Increment retry count for assigned topics
      consumer.assignment().stream()
          .map(TopicPartition::topic)
          .distinct()
          .forEach(topic -> pollRetryLookup.merge(topic, 1, Integer::sum));
          
      if (shouldStopPolling()) {
        LOGGER.info("No new data found after {} retries - polling complete", config.getRetryCount());
      }
    }

    private boolean shouldStopPolling() {
      return pollRetryLookup.values().stream().allMatch(count -> count > config.getRetryCount());
    }

    private void processRecords(final ConsumerRecords<String, byte[]> consumerRecords,
                               final List<ConsumerRecord<String, byte[]>> recordsList) {
      for (final ConsumerRecord<String, byte[]> record : consumerRecords) {
        recordsList.add(record);
        recordCount.incrementAndGet();
        
        if (recordCount.get() >= config.getMaxRecords()) {
          break;
        }
      }
      
      LOGGER.debug("Processed {} records in this batch", consumerRecords.count());
    }

    private void resetRetryCounters() {
      pollRetryLookup.replaceAll((topic, count) -> 0);
    }

    private void commitOffsetsAsync() {
      try {
        consumer.commitAsync((offsets, exception) -> {
          if (exception != null) {
            LOGGER.warn("Failed to commit offsets asynchronously", exception);
          }
        });
      } catch (final Exception e) {
        LOGGER.warn("Error during async commit", e);
      }
    }
  }
}
