/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.google.common.collect.ImmutableSet;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

public enum SnapshotMetadata {

  FIRST,
  FIRST_IN_DATA_COLLECTION,
  LAST_IN_DATA_COLLECTION,
  TRUE,
  LAST,
  FALSE;

  private static final Set<SnapshotMetadata> ENTRIES_OF_SNAPSHOT_EVENTS =
      ImmutableSet.of(TRUE, FIRST, FIRST_IN_DATA_COLLECTION, LAST_IN_DATA_COLLECTION);
  private static final Map<String, SnapshotMetadata> STRING_TO_ENUM;
  static {
    STRING_TO_ENUM = new HashMap<>(12);
    STRING_TO_ENUM.put("true", TRUE);
    STRING_TO_ENUM.put("TRUE", TRUE);
    STRING_TO_ENUM.put("false", FALSE);
    STRING_TO_ENUM.put("FALSE", FALSE);
    STRING_TO_ENUM.put("last", LAST);
    STRING_TO_ENUM.put("LAST", LAST);
    STRING_TO_ENUM.put("first", FIRST);
    STRING_TO_ENUM.put("FIRST", FIRST);
    STRING_TO_ENUM.put("last_in_data_collection", LAST_IN_DATA_COLLECTION);
    STRING_TO_ENUM.put("LAST_IN_DATA_COLLECTION", LAST_IN_DATA_COLLECTION);
    STRING_TO_ENUM.put("first_in_data_collection", FIRST_IN_DATA_COLLECTION);
    STRING_TO_ENUM.put("FIRST_IN_DATA_COLLECTION", FIRST_IN_DATA_COLLECTION);
  }

  public static SnapshotMetadata fromString(final String value) {
    if (STRING_TO_ENUM.containsKey(value)) {
      return STRING_TO_ENUM.get(value);
    }
    throw new RuntimeException("ENUM value not found for " + value);
  }

  public static boolean isSnapshotEventMetadata(final SnapshotMetadata snapshotMetadata) {
    return ENTRIES_OF_SNAPSHOT_EVENTS.contains(snapshotMetadata);
  }

}
