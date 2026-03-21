/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Utility class for extracting partition keys from Airbyte record data. Supports single fields,
 * multiple fields, and nested field access using dot notation.
 */
public class PartitionKeyExtractor {

  private static final String FIELD_DELIMITER = "|";
  private static final String NESTED_FIELD_DELIMITER = "\\.";

  /**
   * Extracts partition key from record data based on configured fields.
   *
   * @param partitionKeyFields comma-separated list of field names (e.g., "user_id" or
   *        "user.id,order_id")
   * @param recordData the JSON record data
   * @return concatenated key string, or null if no fields found
   */
  public static String extractPartitionKey(String partitionKeyFields, JsonNode recordData) {
    if (recordData == null || !recordData.isObject() || partitionKeyFields == null || partitionKeyFields.trim().isEmpty()) {
      return null;
    }

    String[] fields = partitionKeyFields.split(",");
    List<String> keyValues = new ArrayList<>();

    for (String field : fields) {
      String trimmedField = field.trim();
      JsonNode valueNode = recordData;
      for (String part : trimmedField.split("\\.")) {
        valueNode = valueNode.path(part);
      }
      if (!valueNode.isMissingNode() && !valueNode.isNull()) {
        keyValues.add(valueNode.isValueNode() ? valueNode.asText() : valueNode.toString());
      }
    }

    if (keyValues.isEmpty()) {
      return null;
    }

    return String.join(FIELD_DELIMITER, keyValues);
  }

  /**
   * Extracts a single field value from JSON record data. Supports nested field access using dot
   * notation (e.g., "user.id").
   *
   * @param recordData the JSON record data
   * @param fieldName the field name (supports dot notation for nested fields)
   * @return field value as string, or null if not found
   */
  private static String extractFieldValue(JsonNode recordData, String fieldName) {
    if (recordData == null || !recordData.isObject()) {
      return null;
    }

    String[] fieldParts = fieldName.split("\\.");
    JsonNode currentNode = recordData;

    // Navigate through nested fields
    for (String part : fieldParts) {
      if (!currentNode.has(part)) {
        return null;
      }
      currentNode = currentNode.get(part);
      if (currentNode == null || currentNode.isNull()) {
        return null;
      }
    }

    // Convert to string for primitive types, serialize complex objects
    if (currentNode.isValueNode()) {
      return currentNode.asText();
    } else if (currentNode.isObject() || currentNode.isArray()) {
      return currentNode.toString();
    } else {
      return null;
    }
  }

  /**
   * Generates a fallback key using UUID when no partition key is configured or found.
   *
   * @return randomly generated UUID string
   */
  public static String generateFallbackKey() {
    return UUID.randomUUID().toString();
  }

  /**
   * Determines the final partition key to use for a Kafka message.
   *
   * @param partitionKeyFields configured partition key fields (may be null/empty)
   * @param recordData the JSON record data
   * @return partition key string (never null)
   */
  public static String determinePartitionKey(String partitionKeyFields, JsonNode recordData) {
    String partitionKey = extractPartitionKey(partitionKeyFields, recordData);
    return partitionKey != null ? partitionKey : generateFallbackKey();
  }

}
