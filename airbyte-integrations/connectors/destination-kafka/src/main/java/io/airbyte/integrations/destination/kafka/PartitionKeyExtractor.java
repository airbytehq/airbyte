/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utility class for extracting partition keys from Airbyte record data. Supports single fields,
 * multiple fields, and nested field access using dot notation.
 */
public class PartitionKeyExtractor {

  private static final Logger LOGGER = LoggerFactory.getLogger(PartitionKeyExtractor.class);
  private static final String FIELD_DELIMITER = "|";

  // Cache for split field names to optimize performance in hot path
  private static final ConcurrentMap<String, String[]> FIELD_SPLIT_CACHE = new ConcurrentHashMap<>();

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

    // Use cached split result for performance optimization
    String[] fields = FIELD_SPLIT_CACHE.computeIfAbsent(partitionKeyFields, key -> key.split(","));
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
    if (partitionKey != null) {
      LOGGER.debug("Extracted partition key: {}", partitionKey);
      return partitionKey;
    } else {
      LOGGER.debug("No partition key found, generating fallback key");
      return generateFallbackKey();
    }
  }

}
