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
import io.confluent.kafka.schemaregistry.protobuf.ProtobufSchema;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;
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
 * - Schema Registry integration with authentication support
 * - Thread-safe descriptor caching
 * - Configurable polling and retry logic
 * - Protobuf to JSON conversion
 * - Support for Google protobuf well-known types (Timestamp, Struct, Duration, etc.)
 */
public class ProtobufFormat extends AbstractFormat {

  private static final Logger LOGGER = LoggerFactory.getLogger(ProtobufFormat.class);

  // Configuration constants
  private static final String MESSAGE_FORMAT_CONFIG_KEY = "MessageFormat";
  private static final String VALUE_SUBJECT_SUFFIX = "-value";
  private static final String SUBSCRIPTION_TYPE_SUBSCRIBE = "subscribe";
  private static final String SUBSCRIPTION_TYPE_ASSIGN = "assign";
  
  // Schema Registry configuration constants
  // URL template for Buf.build API to fetch protobuf schema files
  // Format: https://buf.build/{module_name}/raw/main/-/{file_name}
  private static final String URL_TEMPLATE = "https://buf.build/%s/raw/main/-/%s";
  // Configuration keys for Buf.build authentication and schema location
  private static final String TOKEN = "buf_token";           // API token for Buf.build authentication
  private static final String MODULE_NAME = "buf_module_name"; // Buf.build module identifier (e.g., "hudhud/hudhudapis")
  private static final String FILE_NAME = "buf_file_name";     // Path to the .proto file within the module
  
  // Configuration field constants
  private static final String REPEATED_CALLS_CONFIG = "repeated_calls";
  private static final String POLLING_TIME_CONFIG = "polling_time";
  private static final String MAX_RECORDS_PROCESS_CONFIG = "max_records_process";
  private static final String TEST_TOPIC_CONFIG = "test_topic";
  private static final String SUBSCRIPTION_CONFIG = "subscription";
  private static final String SUBSCRIPTION_TYPE_CONFIG = "subscription_type";
  private static final String TOPIC_PATTERN_CONFIG = "topic_pattern";
  private static final String TOPIC_PARTITIONS_CONFIG = "topic_partitions";

  // Default configuration values
  private static final int DEFAULT_RETRY_COUNT = 0;
  private static final int DEFAULT_POLLING_TIME_MS = 100;
  private static final int DEFAULT_MAX_RECORDS = 100000;
  private static final int CONFLUENT_MAGIC_BYTE_LENGTH = 5;
  private static final byte CONFLUENT_MAGIC_BYTE = 0;
  
  // Reusable instances for better performance (thread-safe)
  private static final ObjectMapper JSON_MAPPER = new ObjectMapper();
  private static final JsonFormat.Printer PROTOBUF_JSON_PRINTER = JsonFormat.printer()
      .includingDefaultValueFields()
      .preservingProtoFieldNames();

  // Thread-safe caching for descriptors
  private final Map<String, Descriptors.Descriptor> descriptors = new ConcurrentHashMap<>();
  
  // Thread-safe consumer instance
  private volatile KafkaConsumer<String, byte[]> consumer;

  public ProtobufFormat(JsonNode jsonConfig) {
    super(jsonConfig);
  }

  /**
   * Configures Kafka consumer properties for Protobuf message deserialization.
   * Sets up deserializers for key and value.
   *
   * @return Map of Kafka consumer configuration properties
   */
  @Override
  protected Map<String, Object> getKafkaConfig() {
    Map<String, Object> props = super.getKafkaConfig();

    // Configure deserializers
    props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
    props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, ByteArrayDeserializer.class.getName());

    return props;
  }

  /**
   * Creates and configures a Kafka consumer for Protobuf messages.
   * Handles both subscription patterns and topic-partition assignments.
   * Thread-safe implementation using double-checked locking pattern.
   *
   * @return Configured KafkaConsumer instance
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
      
      Map<String, Object> filteredProps = getKafkaConfig();
      consumer = new KafkaConsumer<>(filteredProps);

      final JsonNode subscription = config.get(SUBSCRIPTION_CONFIG);
      LOGGER.info("Kafka subscribe method: {}", subscription.toString());
      
      switch (subscription.get(SUBSCRIPTION_TYPE_CONFIG).asText()) {
        case SUBSCRIPTION_TYPE_SUBSCRIBE -> {
          // Subscribe to topics matching a pattern
          final String topicPattern = subscription.get(TOPIC_PATTERN_CONFIG).asText();
          consumer.subscribe(Pattern.compile(topicPattern));
          topicsToSubscribe = new ConcurrentHashMap<>(consumer.listTopics()).keySet().stream()
              .filter(topic -> topic.matches(topicPattern))
              .collect(Collectors.toSet());
          LOGGER.info("Topic list: {}", topicsToSubscribe);
        }
        case SUBSCRIPTION_TYPE_ASSIGN -> {
          // Assign specific topic-partition combinations
          topicsToSubscribe = ConcurrentHashMap.newKeySet();
          final String topicPartitions = subscription.get(TOPIC_PARTITIONS_CONFIG).asText();
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
        default -> throw new IllegalArgumentException("Unsupported subscription type: " + 
            subscription.get(SUBSCRIPTION_TYPE_CONFIG).asText());
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
   * Creates a separate test consumer to avoid interfering with the main consumer.
   *
   * @return true if connection is successful, false otherwise
   */
  @Override
  public boolean isAccessible() {
    try {
      final String testTopic = config.has(TEST_TOPIC_CONFIG) ? config.get(TEST_TOPIC_CONFIG).asText() : "";
      if (!testTopic.isBlank()) {
        // Create a separate test consumer to avoid resource conflicts
        final Map<String, Object> testProps = getKafkaConfig();
        try (final KafkaConsumer<String, byte[]> testConsumer = new KafkaConsumer<>(testProps)) {
          testConsumer.subscribe(Pattern.compile(testTopic));
          testConsumer.listTopics();
          LOGGER.info("Successfully connected to Kafka brokers for topic '{}'.", testTopic);
        }
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
          Descriptors.Descriptor descriptor = getDescriptorForTopic(topic);
          return CatalogHelpers
              .createAirbyteStream(topic, buildFieldsFromDescriptor(descriptor).toArray(Field[]::new))
              .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
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
   * Handles Google protobuf well-known types like Timestamp and Struct.
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
      case MESSAGE -> getJsonSchemaTypeForMessageField(fieldDescriptor);
      default -> JsonSchemaType.STRING; // STRING, BYTES, ENUM and others
    };
  }

  /**
   * Determines the appropriate JSON Schema type for MESSAGE type fields.
   * Handles Google protobuf well-known types with special mappings.
   *
   * @param fieldDescriptor Protobuf field descriptor for a MESSAGE type
   * @return Corresponding JsonSchemaType
   */
  private JsonSchemaType getJsonSchemaTypeForMessageField(Descriptors.FieldDescriptor fieldDescriptor) {
    String messageTypeName = fieldDescriptor.getMessageType().getFullName();
    
    return switch (messageTypeName) {
      case "google.protobuf.Timestamp" -> {
        LOGGER.debug("Mapping google.protobuf.Timestamp to STRING type");
        yield JsonSchemaType.STRING; // Timestamps are serialized as ISO 8601 strings
      }
      case "google.protobuf.Struct" -> {
        LOGGER.debug("Mapping google.protobuf.Struct to OBJECT type");
        yield JsonSchemaType.OBJECT; // Struct represents a generic JSON object
      }
      case "google.protobuf.Value" -> {
        LOGGER.debug("Mapping google.protobuf.Value to OBJECT type (can hold any JSON value)");
        yield JsonSchemaType.OBJECT; // Value can represent any JSON value
      }
      case "google.protobuf.ListValue" -> {
        LOGGER.debug("Mapping google.protobuf.ListValue to ARRAY type");
        yield JsonSchemaType.ARRAY; // ListValue represents a JSON array
      }
      case "google.protobuf.Duration" -> {
        LOGGER.debug("Mapping google.protobuf.Duration to STRING type");
        yield JsonSchemaType.STRING; // Durations are serialized as strings (e.g., "1.000340012s")
      }
      case "google.protobuf.FieldMask" -> {
        LOGGER.debug("Mapping google.protobuf.FieldMask to STRING type");
        yield JsonSchemaType.STRING; // FieldMask is serialized as comma-separated field paths
      }
      case "google.protobuf.Any" -> {
        LOGGER.debug("Mapping google.protobuf.Any to OBJECT type");
        yield JsonSchemaType.OBJECT; // Any can contain any message type
      }
      case "google.protobuf.Empty" -> {
        LOGGER.debug("Mapping google.protobuf.Empty to OBJECT type");
        yield JsonSchemaType.OBJECT; // Empty message maps to empty object
      }
      // Wrapper types for primitive values
      case "google.protobuf.DoubleValue", "google.protobuf.FloatValue" -> {
        LOGGER.debug("Mapping {} to NUMBER type", messageTypeName);
        yield JsonSchemaType.NUMBER;
      }
      case "google.protobuf.Int64Value", "google.protobuf.UInt64Value", 
           "google.protobuf.Int32Value", "google.protobuf.UInt32Value" -> {
        LOGGER.debug("Mapping {} to INTEGER type", messageTypeName);
        yield JsonSchemaType.INTEGER;
      }
      case "google.protobuf.BoolValue" -> {
        LOGGER.debug("Mapping google.protobuf.BoolValue to BOOLEAN type");
        yield JsonSchemaType.BOOLEAN;
      }
      case "google.protobuf.StringValue", "google.protobuf.BytesValue" -> {
        LOGGER.debug("Mapping {} to STRING type", messageTypeName);
        yield JsonSchemaType.STRING;
      }
      default -> {
        LOGGER.debug("Mapping custom message type '{}' to OBJECT type", messageTypeName);
        yield JsonSchemaType.OBJECT; // Regular message types
      }
    };
  }

  /**
   * Gets or creates a cached descriptor for the given topic.
   * Thread-safe implementation using ConcurrentHashMap.
   *
   * @param topic Topic name
   * @return Protobuf message descriptor
   */
  private Descriptors.Descriptor getDescriptorForTopic(String topic) {
    return descriptors.computeIfAbsent(topic, this::buildDescriptorForTopic);
  }

  /**
   * Fetches and builds a Protobuf Descriptor from Schema Registry for the given subject.
   *
   * @param topic Schema Registry subject name
   * @return Protobuf message descriptor
   * @throws RuntimeException if descriptor building fails
   */
  private Descriptors.Descriptor buildDescriptorForTopic(String topic) {
    String subject = topic + VALUE_SUBJECT_SUFFIX;

    try {
      final JsonNode protobufConfig = config.get(MESSAGE_FORMAT_CONFIG_KEY);

      // Validate required Buf.build configuration parameters
      // All three parameters are mandatory for Buf.build schema fetching
      if (!(protobufConfig.has(TOKEN) && protobufConfig.has(MODULE_NAME) && protobufConfig.has(FILE_NAME))) {
        throw new RuntimeException(
                String.format("The Arguments ['%s', '%s', '%s'] must be set!", TOKEN, MODULE_NAME, FILE_NAME)
        );
      }

      // Extract configuration values for Buf.build API call
      String token = protobufConfig.get(TOKEN).asText();
      String module = protobufConfig.get(MODULE_NAME).asText();
      String file = protobufConfig.get(FILE_NAME).asText();

      // Build HTTP request to fetch protobuf schema from Buf.build
      // Uses bearer token authentication and requests the raw .proto file
      HttpRequest request = HttpRequest.newBuilder()
              .uri(URI.create(String.format(URL_TEMPLATE, module, file)))
              .header("Authorization", "Bearer " + token)
              .header("Content-Type", "application/json")
              .build();

      // Execute HTTP request to Buf.build API with automatic resource management
      try(HttpClient client = HttpClient.newHttpClient()) {

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        // Validate successful response from Buf.build API
        if (response.statusCode() != 200) {
          throw new RuntimeException(
                  String.format(
                          "failed to fetch schema for Module ['%s'] and file name ['%s']\nWith response: %s",
                          module,
                          file,
                          response.body()
                  )
          );
        }

        LOGGER.debug("Status Code: {}", response.statusCode());

        // Parse the raw .proto file content into a ProtobufSchema object
        // The response body contains the actual protobuf schema definition
        ProtobufSchema protobufSchema = new ProtobufSchema(response.body());

        // Build descriptor from the protobuf schema
        Descriptors.Descriptor descriptor = protobufSchema.toDescriptor();

        // Validate that we have a valid descriptor
        if (descriptor == null) {
          throw new RuntimeException("Failed to build descriptor from protobuf schema for subject: " + subject);
        }

        LOGGER.debug("Successfully built descriptor for subject: {}", subject);
        return descriptor;
      }
    } catch (Exception e) {
      LOGGER.error("Error building descriptor from Schema Registry for subject '{}': {}", subject, e.getMessage());
      throw new RuntimeException("Failed to build descriptor for subject: " + subject, e);
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
    final KafkaConsumer<String, byte[]> consumer = getConsumer();
    final List<ConsumerRecord<String, byte[]>> recordsList = new ArrayList<>();
    
    // Configuration parameters
    final int retry = getRetryCount();
    final int pollingTime = getPollingTimeMs();
    final int maxRecords = getMaxRecords();
    
    final AtomicInteger recordCount = new AtomicInteger();
    final Map<String, Integer> pollLookup = new ConcurrentHashMap<>();
    getTopicsToSubscribe().forEach(topic -> pollLookup.put(topic, 0));
    
    // Poll for messages until completion criteria are met
    while (true) {
      final ConsumerRecords<String, byte[]> consumerRecords =
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
    final Iterator<ConsumerRecord<String, byte[]>> iterator = recordsList.iterator();

    return AutoCloseableIterators.fromIterator(new AbstractIterator<>() {
      @Override
      protected AirbyteMessage computeNext() {
        if (iterator.hasNext()) {
          final ConsumerRecord<String, byte[]> record = iterator.next();
          return convertRecordToAirbyteMessage(record, getDescriptorForTopic(record.topic()));
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
    return config.has(REPEATED_CALLS_CONFIG) ? config.get(REPEATED_CALLS_CONFIG).intValue() : DEFAULT_RETRY_COUNT;
  }

  /**
   * Gets the polling time in milliseconds from configuration with default fallback.
   *
   * @return polling time in milliseconds
   */
  private int getPollingTimeMs() {
    return config.has(POLLING_TIME_CONFIG) ? config.get(POLLING_TIME_CONFIG).intValue() : DEFAULT_POLLING_TIME_MS;
  }

  /**
   * Gets the maximum records to process from configuration with default fallback.
   *
   * @return maximum records count
   */
  private int getMaxRecords() {
    return config.has(MAX_RECORDS_PROCESS_CONFIG) ? config.get(MAX_RECORDS_PROCESS_CONFIG).intValue() : DEFAULT_MAX_RECORDS;
  }

  /**
   * Parses raw Kafka message bytes into a Protobuf DynamicMessage.
   * Handles both Confluent format (with magic byte header) and raw protobuf format.
   *
   * @param messageBytes Raw message bytes from Kafka
   * @param descriptor Protobuf message descriptor
   * @return Parsed DynamicMessage
   * @throws InvalidProtocolBufferException if parsing fails
   */
  private DynamicMessage parseProtobufMessage(byte[] messageBytes, Descriptors.Descriptor descriptor)
          throws InvalidProtocolBufferException {
    byte[] protobufBytes;
    
    // Check for Confluent format (magic byte + schema ID + message)
    if (messageBytes.length > CONFLUENT_MAGIC_BYTE_LENGTH && messageBytes[0] == CONFLUENT_MAGIC_BYTE) {
      // The actual protobuf message starts from byte 5 (after magic byte + 4-byte schema ID)
      protobufBytes = new byte[messageBytes.length - CONFLUENT_MAGIC_BYTE_LENGTH];
      System.arraycopy(messageBytes, CONFLUENT_MAGIC_BYTE_LENGTH, protobufBytes, 0, protobufBytes.length);
      LOGGER.debug("Detected Confluent format with magic byte");
    } else {
      // Assume the entire byte array is the protobuf message
      protobufBytes = messageBytes;
      LOGGER.debug("Detected raw Protobuf format");
    }

    // Parse the protobuf message using the descriptor
    return DynamicMessage.parseFrom(descriptor, protobufBytes);
  }

  /**
   * Converts a Kafka ConsumerRecord to an AirbyteMessage.
   * Handles Protobuf to JSON conversion with proper error handling.
   *
   * @param record Kafka consumer record containing raw protobuf bytes
   * @param descriptor Protobuf message descriptor
   * @return AirbyteMessage with converted data
   * @throws RuntimeException if conversion fails
   */
  private AirbyteMessage convertRecordToAirbyteMessage(
          ConsumerRecord<String, byte[]> record,
          Descriptors.Descriptor descriptor) {
    if (record == null) {
      throw new IllegalArgumentException("Consumer record cannot be null");
    }

    byte[] dataBytes = record.value();
    if (dataBytes == null || dataBytes.length == 0) {
      LOGGER.warn("Received null or empty protobuf data for topic: {}, partition: {}, offset: {}",
          record.topic(), record.partition(), record.offset());
      // Return empty JSON object for null values
      return createAirbyteMessage(record.topic(), JSON_MAPPER.createObjectNode());
    }

    JsonNode output;
    try {
      // Convert Protobuf message to JSON
      DynamicMessage protobufData = parseProtobufMessage(dataBytes, descriptor);
      String jsonString = PROTOBUF_JSON_PRINTER.print(protobufData);
      output = JSON_MAPPER.readTree(jsonString);
    } catch (Exception e) {
      LOGGER.error("Failed to convert protobuf message to JSON for topic: {}, partition: {}, offset: {}", 
          record.topic(), record.partition(), record.offset(), e);
      throw new RuntimeException("Protobuf to JSON conversion failed for topic: " + record.topic(), e);
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
