/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static java.util.stream.Collectors.toList;
import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.fail;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Streams;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.AirbyteProtocolType;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.OffsetTime;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.Pair;

/**
 * Utility class to generate human-readable diffs between expected and actual records. Assumes 1s1t
 * output format.
 */
public class RecordDiffer {

  private final Comparator<JsonNode> recordIdentityComparator;
  private final Comparator<JsonNode> recordSortComparator;
  private final Function<JsonNode, String> recordIdentityExtractor;

  /**
   * @param identifyingColumns Which fields constitute a unique record (typically PK+cursor). Do _not_
   *        include extracted_at; it is handled automatically.
   */
  @SafeVarargs
  public RecordDiffer(final Pair<String, AirbyteType>... identifyingColumns) {
    this.recordIdentityComparator = buildIdentityComparator(identifyingColumns);
    this.recordSortComparator = recordIdentityComparator.thenComparing(record -> asString(record.get("_airbyte_raw_id")));
    this.recordIdentityExtractor = buildIdentityExtractor(identifyingColumns);
  }

  /**
   * In the expected records, a SQL null is represented as a JsonNode without that field at all, and a
   * JSON null is represented as a NullNode. For example, in the JSON blob {"name": null}, the `name`
   * field is a JSON null, and the `address` field is a SQL null.
   */
  public void verifySyncResult(List<JsonNode> expectedRawRecords,
                               List<JsonNode> actualRawRecords,
                               List<JsonNode> expectedFinalRecords,
                               List<JsonNode> actualFinalRecords) {
    assertAll(
        () -> diffRawTableRecords(expectedRawRecords, actualRawRecords),
        () -> diffFinalTableRecords(expectedFinalRecords, actualFinalRecords));
  }

  public void diffRawTableRecords(List<JsonNode> expectedRecords, List<JsonNode> actualRecords) {
    String diff = diffRecords(
        expectedRecords.stream().map(RecordDiffer::copyWithLiftedData).collect(toList()),
        actualRecords.stream().map(RecordDiffer::copyWithLiftedData).collect(toList()),
        recordIdentityComparator,
        recordSortComparator,
        recordIdentityExtractor);

    if (!diff.isEmpty()) {
      fail("Raw table was incorrect.\n" + diff);
    }
  }

  public void diffFinalTableRecords(List<JsonNode> expectedRecords, List<JsonNode> actualRecords) {
    String diff = diffRecords(
        expectedRecords,
        actualRecords,
        recordIdentityComparator,
        recordSortComparator,
        recordIdentityExtractor);

    if (!diff.isEmpty()) {
      fail("Final table was incorrect.\n" + diff);
    }
  }

  /**
   * @return A copy of the record, but with all fields in _airbyte_data lifted to the top level.
   */
  private static JsonNode copyWithLiftedData(JsonNode record) {
    ObjectNode copy = record.deepCopy();
    copy.remove("_airbyte_data");
    Streams.stream(record.get("_airbyte_data").fields()).forEach(field -> {
      if (!copy.has(field.getKey())) {
        copy.set(field.getKey(), field.getValue());
      } else {
        // This would only happen if the record has one of the metadata columns (e.g. _airbyte_raw_id)
        // We don't support that in production, so we don't support it here either.
        throw new RuntimeException("Cannot lift field " + field.getKey() + " because it already exists in the record.");
      }
    });
    return copy;
  }

  /**
   * Build a Comparator to detect equality between two records. It first compares all the identifying
   * columns in order, and breaks ties using extracted_at.
   */
  private Comparator<JsonNode> buildIdentityComparator(Pair<String, AirbyteType>[] identifyingColumns) {
    // Start with a noop comparator for convenience
    Comparator<JsonNode> comp = Comparator.comparing(record -> 0);
    for (Pair<String, AirbyteType> column : identifyingColumns) {
      comp = comp.thenComparing(record -> extract(record, column.getKey(), column.getValue()));
    }
    comp = comp.thenComparing(record -> asTimestampWithTimezone(record.get("_airbyte_extracted_at")));
    return comp;
  }

  /**
   * See {@link #buildIdentityComparator(Pair[])} for an explanation of dataExtractor.
   */
  private Function<JsonNode, String> buildIdentityExtractor(Pair<String, AirbyteType>[] identifyingColumns) {
    return record -> Arrays.stream(identifyingColumns)
        .map(column -> getPrintableFieldIfPresent(record, column.getKey()))
        .collect(Collectors.joining(", "))
        + getPrintableFieldIfPresent(record, "_airbyte_extracted_at");
  }

  private static String getPrintableFieldIfPresent(JsonNode record, String field) {
    if (record.has(field)) {
      return field + "=" + record.get(field);
    } else {
      return "";
    }
  }

  /**
   * Generate a human-readable diff between the two lists. Assumes (in general) that two records with
   * the same PK, cursor, and extracted_at are the same record.
   * <p>
   * Verifies that all values specified in the expected records are correct (_including_ raw_id), and
   * that no other fields are present (except for loaded_at and raw_id). We assume that it's
   * impossible to verify loaded_at, since it's generated dynamically; however, we do provide the
   * ability to assert on the exact raw_id if desired; we simply assume that raw_id is always expected
   * to be present.
   *
   * @param identityComparator Returns 0 iff two records are the "same" record (i.e. have the same
   *        PK+cursor+extracted_at)
   * @param sortComparator Behaves identically to identityComparator, but if two records are the same,
   *        breaks that tie using _airbyte_raw_id
   * @param recordIdExtractor Dump the record's PK+cursor+extracted_at into a human-readable string
   * @return The diff, or empty string if there were no differences
   */
  private static String diffRecords(List<JsonNode> originalExpectedRecords,
                                    List<JsonNode> originalActualRecords,
                                    Comparator<JsonNode> identityComparator,
                                    Comparator<JsonNode> sortComparator,
                                    Function<JsonNode, String> recordIdExtractor) {
    List<JsonNode> expectedRecords = originalExpectedRecords.stream().sorted(sortComparator).toList();
    List<JsonNode> actualRecords = originalActualRecords.stream().sorted(sortComparator).toList();

    // Iterate through both lists in parallel and compare each record.
    // Build up an error message listing any incorrect, missing, or unexpected records.
    String message = "";
    int expectedRecordIndex = 0;
    int actualRecordIndex = 0;
    while (expectedRecordIndex < expectedRecords.size() && actualRecordIndex < actualRecords.size()) {
      JsonNode expectedRecord = expectedRecords.get(expectedRecordIndex);
      JsonNode actualRecord = actualRecords.get(actualRecordIndex);
      int compare = identityComparator.compare(expectedRecord, actualRecord);
      if (compare == 0) {
        // These records should be the same. Find the specific fields that are different and move on
        // to the next records in both lists.
        message += diffSingleRecord(recordIdExtractor, expectedRecord, actualRecord);
        expectedRecordIndex++;
        actualRecordIndex++;
      } else if (compare < 0) {
        // The expected record is missing from the actual records. Print it and move on to the next expected
        // record.
        message += "Row was expected but missing: " + expectedRecord + "\n";
        expectedRecordIndex++;
      } else {
        // There's an actual record which isn't present in the expected records. Print it and move on to the
        // next actual record.
        message += "Row was not expected but present: " + actualRecord + "\n";
        actualRecordIndex++;
      }
    }
    // Tail loops in case we reached the end of one list before the other.
    while (expectedRecordIndex < expectedRecords.size()) {
      message += "Row was expected but missing: " + expectedRecords.get(expectedRecordIndex) + "\n";
      expectedRecordIndex++;
    }
    while (actualRecordIndex < actualRecords.size()) {
      message += "Row was not expected but present: " + actualRecords.get(actualRecordIndex) + "\n";
      actualRecordIndex++;
    }

    return message;
  }

  private static String diffSingleRecord(Function<JsonNode, String> recordIdExtractor, JsonNode expectedRecord, JsonNode actualRecord) {
    boolean foundMismatch = false;
    String mismatchedRecordMessage = "Row had incorrect data: " + recordIdExtractor.apply(expectedRecord) + "\n";
    // Iterate through each column in the expected record and compare it to the actual record's value.
    for (String column : Streams.stream(expectedRecord.fieldNames()).sorted().toList()) {
      // For all other columns, we can just compare their values directly.
      JsonNode expectedValue = expectedRecord.get(column);
      JsonNode actualValue = actualRecord.get(column);
      if (!areJsonNodesEquivalent(expectedValue, actualValue)) {
        mismatchedRecordMessage += generateFieldError("column " + column, expectedValue, actualValue);
        foundMismatch = true;
      }
    }
    // Then check the entire actual record for any columns that we weren't expecting.
    LinkedHashMap<String, JsonNode> extraColumns = checkForExtraOrNonNullFields(expectedRecord, actualRecord);
    if (extraColumns.size() > 0) {
      for (Map.Entry<String, JsonNode> extraColumn : extraColumns.entrySet()) {
        mismatchedRecordMessage += generateFieldError("column " + extraColumn.getKey(), null, extraColumn.getValue());
        foundMismatch = true;
      }
    }
    if (foundMismatch) {
      return mismatchedRecordMessage;
    } else {
      return "";
    }
  }

  private static boolean areJsonNodesEquivalent(JsonNode expectedValue, JsonNode actualValue) {
    if (expectedValue == null || actualValue == null) {
      // If one of the values is null, then we expect both of them to be null.
      return expectedValue == null && actualValue == null;
    } else {
      // Otherwise, we need to compare the actual values.
      // This is kind of sketchy, but seems to work fine for the data we have in our test cases.
      return expectedValue.equals(actualValue)
          // equals() expects the two values to be the same class.
          // We need to handle comparisons between e.g. LongNode and IntNode.
          || (expectedValue.isIntegralNumber() && actualValue.isIntegralNumber() && expectedValue.asLong() == actualValue.asLong())
          || (expectedValue.isNumber() && actualValue.isNumber() && expectedValue.asDouble() == actualValue.asDouble());
    }
  }

  /**
   * Verify that all fields in the actual record are present in the expected record. This is primarily
   * relevant for detecting fields that we expected to be null, but actually were not. See
   * {@link BaseTypingDedupingTest#dumpFinalTableRecords(String, String)} for an explanation of how
   * SQL/JSON nulls are represented in the expected record.
   * <p>
   * This has the side benefit of detecting completely unexpected columns, which would be a very weird
   * bug but is probably still useful to catch.
   */
  private static LinkedHashMap<String, JsonNode> checkForExtraOrNonNullFields(JsonNode expectedRecord, JsonNode actualRecord) {
    LinkedHashMap<String, JsonNode> extraFields = new LinkedHashMap<>();
    for (String column : Streams.stream(actualRecord.fieldNames()).sorted().toList()) {
      // loaded_at and raw_id are generated dynamically, so we just ignore them.
      if (!"_airbyte_loaded_at".equals(column) && !"_airbyte_raw_id".equals(column) && !expectedRecord.has(column)) {
        extraFields.put(column, actualRecord.get(column));
      }
    }
    return extraFields;
  }

  /**
   * Produce a pretty-printed error message, e.g. " For column foo, expected 1 but got 2". The leading
   * spaces are intentional, to make the message easier to read when it's embedded in a larger
   * stacktrace.
   */
  private static String generateFieldError(String fieldname, JsonNode expectedValue, JsonNode actualValue) {
    String expectedString = expectedValue == null ? "SQL NULL (i.e. no value)" : expectedValue.toString();
    String actualString = actualValue == null ? "SQL NULL (i.e. no value)" : actualValue.toString();
    return "  For " + fieldname + ", expected " + expectedString + " but got " + actualString + "\n";
  }

  // These asFoo methods are used for sorting records, so their defaults are intended to make broken
  // records stand out.
  private static String asString(JsonNode node) {
    if (node == null || node.isNull()) {
      return "";
    } else if (node.isTextual()) {
      return node.asText();
    } else {
      return Jsons.serialize(node);
    }
  }

  private static double asDouble(JsonNode node) {
    if (node == null || !node.isNumber()) {
      return Double.MIN_VALUE;
    } else {
      return node.longValue();
    }
  }

  private static long asInt(JsonNode node) {
    if (node == null || !node.isIntegralNumber()) {
      return Long.MIN_VALUE;
    } else {
      return node.longValue();
    }
  }

  private static boolean asBoolean(JsonNode node) {
    if (node == null || !node.isBoolean()) {
      return false;
    } else {
      return node.asBoolean();
    }
  }

  private static Instant asTimestampWithTimezone(JsonNode node) {
    if (node == null || !node.isTextual()) {
      return Instant.ofEpochMilli(Long.MIN_VALUE);
    } else {
      try {
        return Instant.parse(node.asText());
      } catch (Exception e) {
        return Instant.ofEpochMilli(Long.MIN_VALUE);
      }
    }
  }

  private static LocalDateTime asTimestampWithoutTimezone(JsonNode node) {
    if (node == null || !node.isTextual()) {
      return LocalDateTime.ofInstant(Instant.ofEpochMilli(Long.MIN_VALUE), ZoneOffset.UTC);
    } else {
      try {
        return LocalDateTime.parse(node.asText());
      } catch (Exception e) {
        return LocalDateTime.ofInstant(Instant.ofEpochMilli(Long.MIN_VALUE), ZoneOffset.UTC);
      }
    }
  }

  private static OffsetTime asTimeWithTimezone(JsonNode node) {
    if (node == null || !node.isTextual()) {
      return OffsetTime.of(0, 0, 0, 0, ZoneOffset.UTC);
    } else {
      return OffsetTime.parse(node.asText());
    }
  }

  private static LocalTime asTimeWithoutTimezone(JsonNode node) {
    if (node == null || !node.isTextual()) {
      return LocalTime.of(0, 0, 0);
    } else {
      try {
        return LocalTime.parse(node.asText());
      } catch (Exception e) {
        return LocalTime.of(0, 0, 0);
      }
    }
  }

  private static LocalDate asDate(JsonNode node) {
    if (node == null || !node.isTextual()) {
      return LocalDate.ofInstant(Instant.ofEpochMilli(Long.MIN_VALUE), ZoneOffset.UTC);
    } else {
      try {
        return LocalDate.parse(node.asText());
      } catch (Exception e) {
        return LocalDate.ofInstant(Instant.ofEpochMilli(Long.MIN_VALUE), ZoneOffset.UTC);
      }
    }
  }

  // Generics? Never heard of 'em. (I'm sorry)
  private static Comparable extract(JsonNode node, String field, AirbyteType type) {
    if (type instanceof AirbyteProtocolType t) {
      return switch (t) {
        case STRING -> asString(node.get(field));
        case NUMBER -> asDouble(node.get(field));
        case INTEGER -> asInt(node.get(field));
        case BOOLEAN -> asBoolean(node.get(field));
        case TIMESTAMP_WITH_TIMEZONE -> asTimestampWithTimezone(node.get(field));
        case TIMESTAMP_WITHOUT_TIMEZONE -> asTimestampWithoutTimezone(node.get(field));
        case TIME_WITH_TIMEZONE -> asTimeWithTimezone(node.get(field));
        case TIME_WITHOUT_TIMEZONE -> asTimeWithoutTimezone(node.get(field));
        case DATE -> asDate(node.get(field));
        case UNKNOWN -> node.toString();
      };
    } else {
      return node.toString();
    }
  }

}
