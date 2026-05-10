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

  // Cache for fully parsed field structure (split by comma and then by dots) to optimize performance
  private static final ConcurrentMap<String, String[][]> PARSED_FIELDS_CACHE = new ConcurrentHashMap<>();

  // Thread-local list to reuse for collecting key values, avoiding per-record allocations
  private static final ThreadLocal<List<String>> KEY_VALUES_LIST = ThreadLocal.withInitial(ArrayList::new);

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

    // Use cached fully parsed fields structure for performance optimization
    String[][] parsedFields = PARSED_FIELDS_CACHE.computeIfAbsent(partitionKeyFields, key -> {
      String[] fields = key.split(",");
      String[][] result = new String[fields.length][];
      for (int i = 0; i < fields.length; i++) {
        result[i] = fields[i].trim().split("\\.");
      }
      return result;
    });

    // Reuse thread-local list to avoid per-record allocations
    List<String> keyValues = KEY_VALUES_LIST.get();
    keyValues.clear();

    for (String[] fieldParts : parsedFields) {
      JsonNode valueNode = recordData;
      for (String part : fieldParts) {
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
