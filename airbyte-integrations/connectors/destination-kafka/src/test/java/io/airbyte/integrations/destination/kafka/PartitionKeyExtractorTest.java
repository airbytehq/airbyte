/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class PartitionKeyExtractorTest {

  private static final ObjectMapper objectMapper = new ObjectMapper();

  @Test
  void testExtractSingleField() throws Exception {
    String json = "{\"user_id\": \"12345\", \"name\": \"John Doe\"}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey("user_id", recordData);
    
    assertEquals("12345", result);
  }

  @Test
  void testExtractMultipleFields() throws Exception {
    String json = "{\"user_id\": \"12345\", \"order_id\": \"67890\", \"name\": \"John Doe\"}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey("user_id,order_id", recordData);
    
    assertEquals("12345|67890", result);
  }

  @Test
  void testExtractNestedField() throws Exception {
    String json = "{\"user\": {\"id\": \"12345\", \"name\": \"John\"}, \"order_id\": \"67890\"}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey("user.id", recordData);
    
    assertEquals("12345", result);
  }

  @Test
  void testExtractMultipleNestedFields() throws Exception {
    String json = "{\"user\": {\"id\": \"12345\", \"email\": \"john@example.com\"}, \"order\": {\"id\": \"67890\"}}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey("user.id,order.id", recordData);
    
    assertEquals("12345|67890", result);
  }

  @Test
  void testExtractMixedFields() throws Exception {
    String json = "{\"user_id\": \"12345\", \"user\": {\"email\": \"john@example.com\"}, \"order_id\": \"67890\"}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey("user_id,user.email,order_id", recordData);
    
    assertEquals("12345|john@example.com|67890", result);
  }

  @Test
  void testMissingField() throws Exception {
    String json = "{\"user_id\": \"12345\", \"name\": \"John Doe\"}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey("missing_field", recordData);
    
    assertNull(result);
  }

  @Test
  void testSomeFieldsMissing() throws Exception {
    String json = "{\"user_id\": \"12345\", \"name\": \"John Doe\"}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey("user_id,missing_field", recordData);
    
    assertEquals("12345", result);
  }

  @Test
  void testMissingNestedField() throws Exception {
    String json = "{\"user\": {\"name\": \"John\"}, \"order_id\": \"67890\"}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey("user.id,order_id", recordData);
    
    assertEquals("67890", result);
  }

  @Test
  void testNullFieldValue() throws Exception {
    String json = "{\"user_id\": null, \"name\": \"John Doe\"}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey("user_id", recordData);
    
    assertNull(result);
  }

  @Test
  void testNumericFieldValue() throws Exception {
    String json = "{\"user_id\": 12345, \"name\": \"John Doe\"}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey("user_id", recordData);
    
    assertEquals("12345", result);
  }

  @Test
  void testBooleanFieldValue() throws Exception {
    String json = "{\"active\": true, \"name\": \"John Doe\"}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey("active", recordData);
    
    assertEquals("true", result);
  }

  @Test
  void testComplexObjectFieldValue() throws Exception {
    String json = "{\"user\": {\"id\": 123, \"name\": \"John\"}, \"name\": \"John Doe\"}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey("user", recordData);
    
    assertEquals("{\"id\":123,\"name\":\"John\"}", result);
  }

  @Test
  void testEmptyPartitionKeyFields() throws Exception {
    String json = "{\"user_id\": \"12345\", \"name\": \"John Doe\"}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey("", recordData);
    
    assertNull(result);
  }

  @Test
  void testNullPartitionKeyFields() throws Exception {
    String json = "{\"user_id\": \"12345\", \"name\": \"John Doe\"}";
    JsonNode recordData = objectMapper.readTree(json);
    
    String result = PartitionKeyExtractor.extractPartitionKey(null, recordData);
    
    assertNull(result);
  }

  @Test
  void testDeterminePartitionKeyWithConfiguredField() throws Exception {
    String json = "{\"user_id\": \"12345\", \"name\": \"John Doe\"}";
    JsonNode recordData = objectMapper.readTree(json);
    String result = PartitionKeyExtractor.determinePartitionKey("user_id", recordData);
    assertEquals("12345", result);
  }

  @Test
  void testDeterminePartitionKeyWithMissingField() throws Exception {
    String json = "{\"user_id\": \"12345\", \"name\": \"John Doe\"}";
    JsonNode recordData = objectMapper.readTree(json);
    String result = PartitionKeyExtractor.determinePartitionKey("missing_field", recordData);
    assertNotNull(result);
    assertTrue(result.matches("^[a-f0-9-]{36}$")); // UUID format
  }

  @Test
  void testDeterminePartitionKeyWithNullConfig() throws Exception {
    String json = "{\"user_id\": \"12345\", \"name\": \"John Doe\"}";
    JsonNode recordData = objectMapper.readTree(json);
    String result = PartitionKeyExtractor.determinePartitionKey(null, recordData);
    assertNotNull(result);
    assertTrue(result.matches("^[a-f0-9-]{36}$")); // UUID format
  }

  @Test
  void testGenerateFallbackKey() {
    String result1 = PartitionKeyExtractor.generateFallbackKey();
    String result2 = PartitionKeyExtractor.generateFallbackKey();
    assertNotNull(result1);
    assertNotNull(result2);
    assertNotEquals(result1, result2);
    assertTrue(result1.matches("^[a-f0-9-]{36}$")); // UUID format
    assertTrue(result2.matches("^[a-f0-9-]{36}$")); // UUID format
  }

  @Test
  void testNullRecordData() throws Exception {
    String result = PartitionKeyExtractor.extractPartitionKey("user_id", null);
    assertNull(result);
  }

  @Test
  void testNonObjectRecordData() throws Exception {
    String result = PartitionKeyExtractor.extractPartitionKey("user_id", objectMapper.readTree("\"string\""));
    assertNull(result);
  }
}
