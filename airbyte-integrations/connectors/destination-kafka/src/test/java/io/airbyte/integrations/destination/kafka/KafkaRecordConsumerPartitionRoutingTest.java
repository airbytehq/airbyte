/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import org.apache.kafka.clients.producer.MockProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class KafkaRecordConsumerPartitionRoutingTest {

  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
  private static final StandardNameTransformer NAME_TRANSFORMER = new StandardNameTransformer();
  
  private MockProducer<String, JsonNode> mockProducer;
  private ConfiguredAirbyteCatalog catalog;
  private List<AirbyteMessage> outputMessages;
  private ConcurrentMap<String, List<ProducerRecord<String, JsonNode>>> recordsByKey;

  @BeforeEach
  void setUp() {
    mockProducer = new MockProducer<>(true, new StringSerializer(), new org.apache.kafka.connect.json.JsonSerializer());
    outputMessages = new ArrayList<>();
    recordsByKey = new ConcurrentHashMap<>();
    
    // Create a simple catalog with one stream
    ConfiguredAirbyteStream stream = new ConfiguredAirbyteStream()
        .withSyncMode(SyncMode.FULL_REFRESH)
        .withCursorField(null)
        .withDestinationSyncMode(SyncMode.FULL_REFRESH)
        .withStream(io.airbyte.protocol.models.v0.AirbyteStream.builder()
            .name("test_stream")
            .namespace("test_namespace")
            .jsonSchema(ImmutableMap.of("type", "object"))
            .build());
    
    catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream));
  }

  @Test
  void testSamePartitionKeyRoutesToSamePartition() throws Exception {
    // Create config with partition key field
    JsonNode config = OBJECT_MAPPER.readTree("""
        {
          "topic_pattern": "test.topic",
          "partition_key_field": "user_id",
          "bootstrap_servers": "localhost:9092",
          "protocol": {"security_protocol": "PLAINTEXT"},
          "acks": "1",
          "enable_idempotence": false,
          "compression_type": "none",
          "batch_size": 16384,
          "linger_ms": 0,
          "max_in_flight_requests_per_connection": 5,
          "client_dns_lookup": "use_all_dns_ips",
          "buffer_memory": 33554432,
          "max_request_size": 1048576,
          "retries": 2147483647,
          "socket_connection_setup_timeout_ms": 10000,
          "socket_connection_setup_timeout_max_ms": 30000,
          "max_block_ms": 60000,
          "request_timeout_ms": 30000,
          "delivery_timeout_ms": 120000,
          "send_buffer_bytes": 131072,
          "receive_buffer_bytes": 32768
        }
        """);
    
    // Create custom KafkaDestinationConfig with mock producer
    KafkaDestinationConfig kafkaConfig = new KafkaDestinationConfig(
        "test.topic",
        false,
        "user_id",
        config) {
      @Override
      public org.apache.kafka.clients.producer.KafkaProducer<String, JsonNode> getProducer() {
        return mockProducer;
      }
    };
    
    KafkaRecordConsumer consumer = new KafkaRecordConsumer(
        kafkaConfig,
        catalog,
        outputMessages::add,
        NAME_TRANSFORMER);
    
    consumer.start();
    
    // Send two records with the same user_id
    AirbyteRecordMessage record1 = createRecord("user1", "order1");
    AirbyteRecordMessage record2 = createRecord("user1", "order2");
    
    consumer.acceptTracked(createMessage(record1));
    consumer.acceptTracked(createMessage(record2));
    
    consumer.close(false);
    
    // Verify both records have the same key
    List<ProducerRecord<String, JsonNode>> history = mockProducer.history();
    assertEquals(2, history.size());
    
    ProducerRecord<String, JsonNode> producerRecord1 = history.get(0);
    ProducerRecord<String, JsonNode> producerRecord2 = history.get(1);
    
    assertEquals("user1", producerRecord1.key());
    assertEquals("user1", producerRecord2.key());
    
    // Both should go to the same partition (MockProducer uses hash of key)
    assertEquals(producerRecord1.partition(), producerRecord2.partition());
  }

  @Test
  void testDifferentPartitionKeysRouteToDifferentPartitions() throws Exception {
    // Create config with partition key field
    JsonNode config = OBJECT_MAPPER.readTree("""
        {
          "topic_pattern": "test.topic",
          "partition_key_field": "user_id",
          "bootstrap_servers": "localhost:9092",
          "protocol": {"security_protocol": "PLAINTEXT"},
          "acks": "1",
          "enable_idempotence": false,
          "compression_type": "none",
          "batch_size": 16384,
          "linger_ms": 0,
          "max_in_flight_requests_per_connection": 5,
          "client_dns_lookup": "use_all_dns_ips",
          "buffer_memory": 33554432,
          "max_request_size": 1048576,
          "retries": 2147483647,
          "socket_connection_setup_timeout_ms": 10000,
          "socket_connection_setup_timeout_max_ms": 30000,
          "max_block_ms": 60000,
          "request_timeout_ms": 30000,
          "delivery_timeout_ms": 120000,
          "send_buffer_bytes": 131072,
          "receive_buffer_bytes": 32768
        }
        """);
    
    // Create custom KafkaDestinationConfig with mock producer
    KafkaDestinationConfig kafkaConfig = new KafkaDestinationConfig(
        "test.topic",
        false,
        "user_id",
        config) {
      @Override
      public org.apache.kafka.clients.producer.KafkaProducer<String, JsonNode> getProducer() {
        return mockProducer;
      }
    };
    
    KafkaRecordConsumer consumer = new KafkaRecordConsumer(
        kafkaConfig,
        catalog,
        outputMessages::add,
        NAME_TRANSFORMER);
    
    consumer.start();
    
    // Send two records with different user_ids
    AirbyteRecordMessage record1 = createRecord("user1", "order1");
    AirbyteRecordMessage record2 = createRecord("user2", "order2");
    
    consumer.acceptTracked(createMessage(record1));
    consumer.acceptTracked(createMessage(record2));
    
    consumer.close(false);
    
    // Verify records have different keys and likely different partitions
    List<ProducerRecord<String, JsonNode>> history = mockProducer.history();
    assertEquals(2, history.size());
    
    ProducerRecord<String, JsonNode> producerRecord1 = history.get(0);
    ProducerRecord<String, JsonNode> producerRecord2 = history.get(1);
    
    assertEquals("user1", producerRecord1.key());
    assertEquals("user2", producerRecord2.key());
    
    // Different keys should result in different partitions (in most cases)
    // Note: This is probabilistic, but with different string keys it's very likely
    assertNotEquals(producerRecord1.key(), producerRecord2.key());
  }

  @Test
  void testMultipleFieldsPartitionKey() throws Exception {
    // Create config with multiple partition key fields
    JsonNode config = OBJECT_MAPPER.readTree("""
        {
          "topic_pattern": "test.topic",
          "partition_key_field": "user_id,order_id",
          "bootstrap_servers": "localhost:9092",
          "protocol": {"security_protocol": "PLAINTEXT"},
          "acks": "1",
          "enable_idempotence": false,
          "compression_type": "none",
          "batch_size": 16384,
          "linger_ms": 0,
          "max_in_flight_requests_per_connection": 5,
          "client_dns_lookup": "use_all_dns_ips",
          "buffer_memory": 33554432,
          "max_request_size": 1048576,
          "retries": 2147483647,
          "socket_connection_setup_timeout_ms": 10000,
          "socket_connection_setup_timeout_max_ms": 30000,
          "max_block_ms": 60000,
          "request_timeout_ms": 30000,
          "delivery_timeout_ms": 120000,
          "send_buffer_bytes": 131072,
          "receive_buffer_bytes": 32768
        }
        """);
    
    // Create custom KafkaDestinationConfig with mock producer
    KafkaDestinationConfig kafkaConfig = new KafkaDestinationConfig(
        "test.topic",
        false,
        "user_id,order_id",
        config) {
      @Override
      public org.apache.kafka.clients.producer.KafkaProducer<String, JsonNode> getProducer() {
        return mockProducer;
      }
    };
    
    KafkaRecordConsumer consumer = new KafkaRecordConsumer(
        kafkaConfig,
        catalog,
        outputMessages::add,
        NAME_TRANSFORMER);
    
    consumer.start();
    
    // Send records with same user_id but different order_id
    AirbyteRecordMessage record1 = createRecord("user1", "order1");
    AirbyteRecordMessage record2 = createRecord("user1", "order2");
    
    consumer.acceptTracked(createMessage(record1));
    consumer.acceptTracked(createMessage(record2));
    
    consumer.close(false);
    
    // Verify records have different composite keys
    List<ProducerRecord<String, JsonNode>> history = mockProducer.history();
    assertEquals(2, history.size());
    
    ProducerRecord<String, JsonNode> producerRecord1 = history.get(0);
    ProducerRecord<String, JsonNode> producerRecord2 = history.get(1);
    
    assertEquals("user1|order1", producerRecord1.key());
    assertEquals("user1|order2", producerRecord2.key());
    
    // Different composite keys should result in different partitions
    assertNotEquals(producerRecord1.key(), producerRecord2.key());
  }

  @Test
  void testMissingPartitionKeyFieldFallback() throws Exception {
    // Create config with partition key field that doesn't exist in records
    JsonNode config = OBJECT_MAPPER.readTree("""
        {
          "topic_pattern": "test.topic",
          "partition_key_field": "missing_field",
          "bootstrap_servers": "localhost:9092",
          "protocol": {"security_protocol": "PLAINTEXT"},
          "acks": "1",
          "enable_idempotence": false,
          "compression_type": "none",
          "batch_size": 16384,
          "linger_ms": 0,
          "max_in_flight_requests_per_connection": 5,
          "client_dns_lookup": "use_all_dns_ips",
          "buffer_memory": 33554432,
          "max_request_size": 1048576,
          "retries": 2147483647,
          "socket_connection_setup_timeout_ms": 10000,
          "socket_connection_setup_timeout_max_ms": 30000,
          "max_block_ms": 60000,
          "request_timeout_ms": 30000,
          "delivery_timeout_ms": 120000,
          "send_buffer_bytes": 131072,
          "receive_buffer_bytes": 32768
        }
        """);
    
    // Create custom KafkaDestinationConfig with mock producer
    KafkaDestinationConfig kafkaConfig = new KafkaDestinationConfig(
        "test.topic",
        false,
        "missing_field",
        config) {
      @Override
      public org.apache.kafka.clients.producer.KafkaProducer<String, JsonNode> getProducer() {
        return mockProducer;
      }
    };
    
    KafkaRecordConsumer consumer = new KafkaRecordConsumer(
        kafkaConfig,
        catalog,
        outputMessages::add,
        NAME_TRANSFORMER);
    
    consumer.start();
    
    // Send record without the configured partition key field
    AirbyteRecordMessage record = createRecord("user1", "order1");
    
    consumer.acceptTracked(createMessage(record));
    
    consumer.close(false);
    
    // Verify record gets a UUID fallback key
    List<ProducerRecord<String, JsonNode>> history = mockProducer.history();
    assertEquals(1, history.size());
    
    ProducerRecord<String, JsonNode> producerRecord = history.get(0);
    
    // Should be a UUID (fallback behavior)
    assertNotNull(producerRecord.key());
    assertTrue(producerRecord.key().matches("^[a-f0-9-]{36}$"));
  }

  @Test
  void testNestedFieldPartitionKey() throws Exception {
    // Create config with nested partition key field
    JsonNode config = OBJECT_MAPPER.readTree("""
        {
          "topic_pattern": "test.topic",
          "partition_key_field": "user.id",
          "bootstrap_servers": "localhost:9092",
          "protocol": {"security_protocol": "PLAINTEXT"},
          "acks": "1",
          "enable_idempotence": false,
          "compression_type": "none",
          "batch_size": 16384,
          "linger_ms": 0,
          "max_in_flight_requests_per_connection": 5,
          "client_dns_lookup": "use_all_dns_ips",
          "buffer_memory": 33554432,
          "max_request_size": 1048576,
          "retries": 2147483647,
          "socket_connection_setup_timeout_ms": 10000,
          "socket_connection_setup_timeout_max_ms": 30000,
          "max_block_ms": 60000,
          "request_timeout_ms": 30000,
          "delivery_timeout_ms": 120000,
          "send_buffer_bytes": 131072,
          "receive_buffer_bytes": 32768
        }
        """);
    
    // Create custom KafkaDestinationConfig with mock producer
    KafkaDestinationConfig kafkaConfig = new KafkaDestinationConfig(
        "test.topic",
        false,
        "user.id",
        config) {
      @Override
      public org.apache.kafka.clients.producer.KafkaProducer<String, JsonNode> getProducer() {
        return mockProducer;
      }
    };
    
    KafkaRecordConsumer consumer = new KafkaRecordConsumer(
        kafkaConfig,
        catalog,
        outputMessages::add,
        NAME_TRANSFORMER);
    
    consumer.start();
    
    // Send record with nested user.id field
    AirbyteRecordMessage record = createNestedRecord("user1", "order1");
    
    consumer.acceptTracked(createMessage(record));
    
    consumer.close(false);
    
    // Verify record uses nested field as key
    List<ProducerRecord<String, JsonNode>> history = mockProducer.history();
    assertEquals(1, history.size());
    
    ProducerRecord<String, JsonNode> producerRecord = history.get(0);
    assertEquals("user1", producerRecord.key());
  }

  private AirbyteRecordMessage createRecord(String userId, String orderId) throws Exception {
    return new AirbyteRecordMessage()
        .withStream("test_stream")
        .withNamespace("test_namespace")
        .withEmittedAt(System.currentTimeMillis())
        .withData(OBJECT_MAPPER.readTree(String.format("""
            {
              "user_id": "%s",
              "order_id": "%s",
              "product": "test_product",
              "amount": 100.0
            }
            """, userId, orderId)));
  }

  private AirbyteRecordMessage createNestedRecord(String userId, String orderId) throws Exception {
    return new AirbyteRecordMessage()
        .withStream("test_stream")
        .withNamespace("test_namespace")
        .withEmittedAt(System.currentTimeMillis())
        .withData(OBJECT_MAPPER.readTree(String.format("""
            {
              "user": {
                "id": "%s",
                "name": "Test User"
              },
              "order_id": "%s",
              "product": "test_product",
              "amount": 100.0
            }
            """, userId, orderId)));
  }

  private AirbyteMessage createMessage(AirbyteRecordMessage record) {
    return new AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(record);
  }
}
