package io.airbyte.integrations.base.destination.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
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
import java.util.Objects;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.Pair;

/**
 * Utility class to generate human-readable diffs between expected and actual records. Assumes 1s1t output format.
 */
public class RecordDiffer {

  private final Comparator<JsonNode> rawRecordIdentityComparator;
  private final Comparator<JsonNode> rawRecordSortComparator;
  private final Function<JsonNode, String> rawRecordIdentityExtractor;
  private final Comparator<JsonNode> finalRecordIdentityComparator;
  private final Comparator<JsonNode> finalRecordSortComparator;
  private final Function<JsonNode, String> finalRecordIdentityExtractor;

  public RecordDiffer(Pair<String, AirbyteType>... columns) {
    // Start with a noop comparator for convenience
    Comparator<JsonNode> rawIdComp = Comparator.comparing(record -> 0);
    Comparator<JsonNode> finalIdComp = Comparator.comparing(record -> 0);
    for (Pair<String, AirbyteType> column : columns) {
      rawIdComp = rawIdComp.thenComparing(record -> extract(record.get("_airbyte_data"), column.getKey(), column.getValue()));
      finalIdComp = finalIdComp.thenComparing(record -> extract(record, column.getKey(), column.getValue()));
    }
    this.rawRecordIdentityComparator = rawIdComp.thenComparing(record -> asTimestampWithTimezone(record.get("_airbyte_extracted_at")));
    this.rawRecordSortComparator = rawRecordIdentityComparator.thenComparing(record -> asString(record.get("_airbyte_raw_id")));
    this.finalRecordIdentityComparator = finalIdComp.thenComparing(record -> asTimestampWithTimezone(record.get("_airbyte_extracted_at")));
    this.finalRecordSortComparator = finalRecordIdentityComparator.thenComparing(record -> asString(record.get("_airbyte_raw_id")));

    rawRecordIdentityExtractor = record -> Arrays.stream(columns)
        .map(column -> getPrintableFieldIfPresent(record.get("_airbyte_data"), column.getKey()))
        .collect(Collectors.joining("; "))
        + getPrintableFieldIfPresent(record, "_airbyte_extracted_at");
    finalRecordIdentityExtractor = record -> Arrays.stream(columns)
        .map(column -> getPrintableFieldIfPresent(record, column.getKey()))
        .collect(Collectors.joining("; "))
        + getPrintableFieldIfPresent(record, "_airbyte_extracted_at");
  }

  /**
   * In the expected records, a SQL null is represented as a JsonNode without that field at all, and a JSON null is
   * represented as a NullNode. For example, in the JSON blob {"name":  null}, the `name` field is a JSON null, and the
   * `address` field is a SQL null.
   */
  public void verifySyncResult(List<JsonNode> expectedRawRecords,
                               List<JsonNode> actualRawRecords,
                               List<JsonNode> expectedFinalRecords,
                               List<JsonNode> actualFinalRecords) {
    assertAll(
        () -> diffRawTableRecords(expectedRawRecords, actualRawRecords),
        () -> diffFinalTableRecords(expectedFinalRecords, actualFinalRecords)
    );
  }

  public void diffRawTableRecords(List<JsonNode> expectedRecords, List<JsonNode> actualRecords) {
    String diff = diffRecords(
        expectedRecords,
        actualRecords,
        rawRecordIdentityComparator,
        rawRecordSortComparator,
        rawRecordIdentityExtractor,
        true);

    assertTrue(diff.isEmpty(), "Raw table was incorrect.\n" + diff);
  }

  public void diffFinalTableRecords(List<JsonNode> expectedRecords, List<JsonNode> actualRecords) {
    String diff = diffRecords(
        expectedRecords,
        actualRecords,
        finalRecordIdentityComparator,
        finalRecordSortComparator,
        finalRecordIdentityExtractor,
        false);

    assertTrue(diff.isEmpty(), "Final table was incorrect.\n" + diff);
  }

  private static String getPrintableFieldIfPresent(JsonNode record, String field) {
    if (record.has(field)) {
      return field + "=" + record.get(field) + "; ";
    } else {
      return "";
    }
  }

  /**
   * Generate a human-readable diff between the two lists. Only checks the keys specified in
   * expectedRecords. Assumes (in general) that two records with the same PK, cursor, and extracted_at
   * are the same record.
   *
   * @param identityComparator Returns 0 iff two records are the "same" record (i.e. have the same
   *        PK+cursor+extracted_at)
   * @param sortComparator Behaves identically to identityComparator, but if two records are the same,
   *        breaks that tie using _airbyte_raw_id
   * @param recordIdExtractor Dump the record's PK+cursor+extracted_at into a human-readable string
   * @param extractRawData Whether to look inside the _airbyte_data column and diff its subfields
   * @return The diff, or empty string if there were no differences
   */
  private static String diffRecords(List<JsonNode> originalExpectedRecords,
                                    List<JsonNode> originalActualRecords,
                                    Comparator<JsonNode> identityComparator,
                                    Comparator<JsonNode> sortComparator,
                                    Function<JsonNode, String> recordIdExtractor,
                                    boolean extractRawData) {
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
        // These records should be the same. Find the specific fields that are different.
        boolean foundMismatch = false;
        String mismatchedRecordMessage = "Row had incorrect data:" + recordIdExtractor.apply(expectedRecord) + "\n";
        // Iterate through each column in the expected record and compare it to the actual record's value.
        for (String column : Streams.stream(expectedRecord.fieldNames()).sorted().toList()) {
          if (extractRawData && "_airbyte_data".equals(column)) {
            // For the raw data in particular, we should also diff the fields inside _airbyte_data.
            JsonNode expectedRawData = expectedRecord.get("_airbyte_data");
            JsonNode actualRawData = actualRecord.get("_airbyte_data");
            // Iterate through all the subfields of the expected raw data and check that they match the actual
            // record...
            for (String field : Streams.stream(expectedRawData.fieldNames()).sorted().toList()) {
              JsonNode expectedValue = expectedRawData.get(field);
              JsonNode actualValue = actualRawData.get(field);
              if (jsonNodesNotEquivalent(expectedValue, actualValue)) {
                mismatchedRecordMessage += generateFieldError("_airbyte_data." + field, expectedValue, actualValue);
                foundMismatch = true;
              }
            }
            // ... and then check the actual raw data for any subfields that we weren't expecting.
            LinkedHashMap<String, JsonNode> extraColumns = checkForExtraOrNonNullFields(expectedRawData, actualRawData);
            if (extraColumns.size() > 0) {
              for (Map.Entry<String, JsonNode> extraColumn : extraColumns.entrySet()) {
                mismatchedRecordMessage += generateFieldError("_airbyte_data." + extraColumn.getKey(), null, extraColumn.getValue());
                foundMismatch = true;
              }
            }
          } else {
            // For all other columns, we can just compare their values directly.
            JsonNode expectedValue = expectedRecord.get(column);
            JsonNode actualValue = actualRecord.get(column);
            if (jsonNodesNotEquivalent(expectedValue, actualValue)) {
              mismatchedRecordMessage += generateFieldError("column " + column, expectedValue, actualValue);
              foundMismatch = true;
            }
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
          message += mismatchedRecordMessage;
        }

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

  private static boolean jsonNodesNotEquivalent(JsonNode expectedValue, JsonNode actualValue) {
    // This is kind of sketchy, but seems to work fine for the data we have in our test cases.
    return !Objects.equals(expectedValue, actualValue)
        // Objects.equals expects the two values to be the same class.
        // We need to handle comparisons between e.g. LongNode and IntNode.
        && !(expectedValue.isIntegralNumber() && actualValue.isIntegralNumber() && expectedValue.asLong() == actualValue.asLong())
        && !(expectedValue.isNumber() && actualValue.isNumber() && expectedValue.asDouble() == actualValue.asDouble());
  }

  /**
   * Verify that all fields in the actual record are present in the expected record. This is primarily
   * relevant for detecting fields that we expected to be null, but actually were not. See
   * {@link BaseTypingDedupingTest#dumpFinalTableRecords(String, String)} for an explanation of how SQL/JSON nulls are
   * represented in the expected record.
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
   * Produce a pretty-printed error message, e.g. " For column foo, expected 1 but got 2". The leading spaces are
   * intentional, to make the message easier to read when it's embedded in a larger stacktrace.
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
