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
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class KafkaRecordConsumerPartitionRoutingTest {

  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
  private static final StandardNameTransformer NAME_TRANSFORMER = new StandardNameTransformer();
  
  private ConfiguredAirbyteCatalog catalog;
  private List<AirbyteMessage> outputMessages;

  @BeforeEach
  void setUp() {
    outputMessages = new ArrayList<>();
    
    // Create a simple catalog with one stream
    AirbyteStream airbyteStream = new AirbyteStream()
        .withName("test_stream")
        .withNamespace("test_namespace")
        .withJsonSchema(OBJECT_MAPPER.valueToTree(ImmutableMap.of("type", "object")));
    
    ConfiguredAirbyteStream stream = new ConfiguredAirbyteStream()
        .withSyncMode(SyncMode.FULL_REFRESH)
        .withCursorField(null)
        .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
        .withStream(airbyteStream);
    
    catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream));
  }

  @Test
  void testPartitionKeyExtraction() throws Exception {
    // Test partition key extraction directly
    String recordJson = """
        {
          "user_id": "user123",
          "order_id": "order456",
          "product": "laptop",
          "amount": 999.99
        }
        """;
    
    JsonNode recordData = OBJECT_MAPPER.readTree(recordJson);
    
    // Test single field extraction
    String singleKey = PartitionKeyExtractor.extractPartitionKey("user_id", recordData);
    assertEquals("user123", singleKey);
    
    // Test multiple field extraction
    String multiKey = PartitionKeyExtractor.extractPartitionKey("user_id,order_id", recordData);
    assertEquals("user123|order456", multiKey);
    
    // Test missing field fallback
    String missingKey = PartitionKeyExtractor.extractPartitionKey("missing_field", recordData);
    assertNull(missingKey);
    
    // Test final key determination (should use UUID fallback for missing field)
    String finalKey = PartitionKeyExtractor.determinePartitionKey("missing_field", recordData);
    assertNotNull(finalKey);
    assertTrue(finalKey.matches("^[a-f0-9-]{36}$")); // UUID format
  }

  @Test
  void testNestedFieldPartitionKey() throws Exception {
    String recordJson = """
        {
          "user": {
            "id": "user123",
            "name": "John Doe"
          },
          "order_id": "order456",
          "product": "laptop"
        }
        """;
    
    JsonNode recordData = OBJECT_MAPPER.readTree(recordJson);
    
    // Test nested field extraction
    String nestedKey = PartitionKeyExtractor.extractPartitionKey("user.id", recordData);
    assertEquals("user123", nestedKey);
  }

  @Test
  void testMixedFieldsPartitionKey() throws Exception {
    String recordJson = """
        {
          "user_id": "user123",
          "user": {
            "email": "john@example.com"
          },
          "order_id": "order456"
        }
        """;
    
    JsonNode recordData = OBJECT_MAPPER.readTree(recordJson);
    
    // Test mixed field extraction
    String mixedKey = PartitionKeyExtractor.extractPartitionKey("user_id,user.email,order_id", recordData);
    assertEquals("user123|john@example.com|order456", mixedKey);
  }

  @Test
  void testNullValueHandling() throws Exception {
    String recordJson = """
        {
          "user_id": null,
          "order_id": "order456",
          "product": "laptop"
        }
        """;
    
    JsonNode recordData = OBJECT_MAPPER.readTree(recordJson);
    
    // Test null field handling
    String nullKey = PartitionKeyExtractor.extractPartitionKey("user_id", recordData);
    assertNull(nullKey);
    
    // Test combination with null field
    String mixedKey = PartitionKeyExtractor.extractPartitionKey("user_id,order_id", recordData);
    assertEquals("order456", mixedKey); // Should only include non-null field
  }

  @Test
  void testConfigurationParsing() throws Exception {
    // Test that configuration parsing works correctly
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
    
    // Test config parsing
    KafkaDestinationConfig kafkaConfig = KafkaDestinationConfig.getKafkaDestinationConfig(config);
    
    assertEquals("test.topic", kafkaConfig.getTopicPattern());
    assertEquals("user_id", kafkaConfig.getPartitionKeyField());
    assertFalse(kafkaConfig.isSync());
  }

  @Test
  void testConfigurationWithoutPartitionKey() throws Exception {
    // Test configuration without partition key field
    JsonNode config = OBJECT_MAPPER.readTree("""
        {
          "topic_pattern": "test.topic",
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
    
    KafkaDestinationConfig kafkaConfig = KafkaDestinationConfig.getKafkaDestinationConfig(config);
    
    assertEquals("test.topic", kafkaConfig.getTopicPattern());
    assertNull(kafkaConfig.getPartitionKeyField()); // Should be null when not configured
  }
}
