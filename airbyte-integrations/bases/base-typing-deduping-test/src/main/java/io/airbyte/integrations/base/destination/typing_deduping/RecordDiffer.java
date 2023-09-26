/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static java.util.stream.Collectors.toList;
import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.fail;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Streams;
import io.airbyte.commons.json.Jsons;
import java.math.BigDecimal;
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
import java.util.stream.IntStream;
import java.util.stream.Stream;
import org.apache.commons.lang3.tuple.Pair;

/**
 * Utility class to generate human-readable diffs between expected and actual records. Assumes 1s1t
 * output format.
 */
public class RecordDiffer {

  private final Comparator<JsonNode> rawRecordIdentityComparator;
  private final Comparator<JsonNode> rawRecordSortComparator;
  private final Function<JsonNode, String> rawRecordIdentityExtractor;
  private final Map<String, String> rawRecordColumnNames;

  private final Comparator<JsonNode> finalRecordIdentityComparator;
  private final Comparator<JsonNode> finalRecordSortComparator;
  private final Function<JsonNode, String> finalRecordIdentityExtractor;
  private final Map<String, String> finalRecordColumnNames;

  /**
   * @param rawRecordColumnNames
   * @param finalRecordColumnNames
   * @param identifyingColumns Which fields constitute a unique record (typically PK+cursor). Do _not_
   *        include extracted_at; it is handled automatically.
   */
  @SafeVarargs
  public RecordDiffer(final Map<String, String> rawRecordColumnNames,
                      final Map<String, String> finalRecordColumnNames,
                      final Pair<ColumnId, AirbyteType>... identifyingColumns) {
    this.rawRecordColumnNames = rawRecordColumnNames;
    this.finalRecordColumnNames = finalRecordColumnNames;
    final Pair<String, AirbyteType>[] rawTableIdentifyingColumns = Arrays.stream(identifyingColumns)
        .map(p -> Pair.of(
            // Raw tables always retain the original column names
            p.getLeft().originalName(),
            p.getRight()))
        .toArray(Pair[]::new);
    this.rawRecordIdentityComparator = buildIdentityComparator(rawTableIdentifyingColumns, rawRecordColumnNames);
    this.rawRecordSortComparator = rawRecordIdentityComparator
        .thenComparing(record -> asString(record.get(getMetadataColumnName(rawRecordColumnNames, "_airbyte_raw_id"))));
    this.rawRecordIdentityExtractor = buildIdentityExtractor(rawTableIdentifyingColumns, rawRecordColumnNames);

    final Pair<String, AirbyteType>[] finalTableIdentifyingColumns = Arrays.stream(identifyingColumns)
        .map(p -> Pair.of(
            // Final tables may have modified the column names, so use the final name here.
            p.getLeft().name(),
            p.getRight()))
        .toArray(Pair[]::new);
    this.finalRecordIdentityComparator = buildIdentityComparator(finalTableIdentifyingColumns, finalRecordColumnNames);
    this.finalRecordSortComparator = finalRecordIdentityComparator
        .thenComparing(record -> asString(record.get(getMetadataColumnName(finalRecordColumnNames, "_airbyte_raw_id"))));
    this.finalRecordIdentityExtractor = buildIdentityExtractor(finalTableIdentifyingColumns, finalRecordColumnNames);
  }

  /**
   * In the expected records, a SQL null is represented as a JsonNode without that field at all, and a
   * JSON null is represented as a NullNode. For example, in the JSON blob {"name": null}, the `name`
   * field is a JSON null, and the `address` field is a SQL null.
   */
  public void verifySyncResult(final List<JsonNode> expectedRawRecords,
                               final List<JsonNode> actualRawRecords,
                               final List<JsonNode> expectedFinalRecords,
                               final List<JsonNode> actualFinalRecords) {
    assertAll(
        () -> diffRawTableRecords(expectedRawRecords, actualRawRecords),
        () -> diffFinalTableRecords(expectedFinalRecords, actualFinalRecords));
  }

  public void diffRawTableRecords(final List<JsonNode> expectedRecords, final List<JsonNode> actualRecords) {
    final String diff = diffRecords(
        expectedRecords.stream().map(this::copyWithLiftedData).collect(toList()),
        actualRecords.stream().map(this::copyWithLiftedData).collect(toList()),
        rawRecordIdentityComparator,
        rawRecordSortComparator,
        rawRecordIdentityExtractor,
        rawRecordColumnNames);

    if (!diff.isEmpty()) {
      fail("Raw table was incorrect.\n" + diff);
    }
  }

  public void diffFinalTableRecords(final List<JsonNode> expectedRecords, final List<JsonNode> actualRecords) {
    final String diff = diffRecords(
        expectedRecords,
        actualRecords,
        finalRecordIdentityComparator,
        finalRecordSortComparator,
        finalRecordIdentityExtractor,
        finalRecordColumnNames);

    if (!diff.isEmpty()) {
      fail("Final table was incorrect.\n" + diff);
    }
  }

  /**
   * Lift _airbyte_data fields to the root level. If _airbyte_data is a string, deserialize it first.
   *
   * @return A copy of the record, but with all fields in _airbyte_data lifted to the top level.
   */
  private JsonNode copyWithLiftedData(final JsonNode record) {
    final ObjectNode copy = record.deepCopy();
    copy.remove(getMetadataColumnName(rawRecordColumnNames, "_airbyte_data"));
    JsonNode airbyteData = record.get(getMetadataColumnName(rawRecordColumnNames, "_airbyte_data"));
    if (airbyteData.isTextual()) {
      airbyteData = Jsons.deserializeExact(airbyteData.asText());
    }
    Streams.stream(airbyteData.fields()).forEach(field -> {
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
  private Comparator<JsonNode> buildIdentityComparator(final Pair<String, AirbyteType>[] identifyingColumns, final Map<String, String> columnNames) {
    // Start with a noop comparator for convenience
    Comparator<JsonNode> comp = Comparator.comparing(record -> 0);
    for (final Pair<String, AirbyteType> column : identifyingColumns) {
      comp = comp.thenComparing(record -> extract(record, column.getKey(), column.getValue()));
    }
    comp = comp.thenComparing(record -> asTimestampWithTimezone(record.get(getMetadataColumnName(columnNames, "_airbyte_extracted_at"))));
    return comp;
  }

  /**
   * See {@link #buildIdentityComparator(Pair[], Map<String, String>)} for an explanation of
   * dataExtractor.
   */
  private Function<JsonNode, String> buildIdentityExtractor(final Pair<String, AirbyteType>[] identifyingColumns,
                                                            final Map<String, String> columnNames) {
    return record -> Arrays.stream(identifyingColumns)
        .map(column -> getPrintableFieldIfPresent(record, column.getKey()))
        .collect(Collectors.joining(", "))
        + getPrintableFieldIfPresent(record, getMetadataColumnName(columnNames, "_airbyte_extracted_at"));
  }

  private static String getPrintableFieldIfPresent(final JsonNode record, final String field) {
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
  private String diffRecords(final List<JsonNode> originalExpectedRecords,
                             final List<JsonNode> originalActualRecords,
                             final Comparator<JsonNode> identityComparator,
                             final Comparator<JsonNode> sortComparator,
                             final Function<JsonNode, String> recordIdExtractor,
                             final Map<String, String> columnNames) {
    final List<JsonNode> expectedRecords = originalExpectedRecords.stream().sorted(sortComparator).toList();
    final List<JsonNode> actualRecords = originalActualRecords.stream().sorted(sortComparator).toList();

    // Iterate through both lists in parallel and compare each record.
    // Build up an error message listing any incorrect, missing, or unexpected records.
    String message = "";
    int expectedRecordIndex = 0;
    int actualRecordIndex = 0;
    while (expectedRecordIndex < expectedRecords.size() && actualRecordIndex < actualRecords.size()) {
      final JsonNode expectedRecord = expectedRecords.get(expectedRecordIndex);
      final JsonNode actualRecord = actualRecords.get(actualRecordIndex);
      final int compare = identityComparator.compare(expectedRecord, actualRecord);
      if (compare == 0) {
        // These records should be the same. Find the specific fields that are different and move on
        // to the next records in both lists.
        message += diffSingleRecord(recordIdExtractor, expectedRecord, actualRecord, columnNames);
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

  private String diffSingleRecord(final Function<JsonNode, String> recordIdExtractor,
                                  final JsonNode expectedRecord,
                                  final JsonNode actualRecord,
                                  final Map<String, String> columnNames) {
    boolean foundMismatch = false;
    String mismatchedRecordMessage = "Row had incorrect data: " + recordIdExtractor.apply(expectedRecord) + "\n";
    // Iterate through each column in the expected record and compare it to the actual record's value.
    for (final String column : Streams.stream(expectedRecord.fieldNames()).sorted().toList()) {
      // For all other columns, we can just compare their values directly.
      final JsonNode expectedValue = expectedRecord.get(column);
      final JsonNode actualValue = actualRecord.get(column);
      if (!areJsonNodesEquivalent(expectedValue, actualValue)) {
        mismatchedRecordMessage += generateFieldError("column " + column, expectedValue, actualValue);
        foundMismatch = true;
      }
    }
    // Then check the entire actual record for any columns that we weren't expecting.
    final LinkedHashMap<String, JsonNode> extraColumns = checkForExtraOrNonNullFields(expectedRecord, actualRecord, columnNames);
    if (extraColumns.size() > 0) {
      for (final Map.Entry<String, JsonNode> extraColumn : extraColumns.entrySet()) {
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

  private static boolean areJsonNodesEquivalent(final JsonNode expectedValue, final JsonNode actualValue) {
    if (expectedValue == null || actualValue == null) {
      // If one of the values is null, then we expect both of them to be null.
      return expectedValue == null && actualValue == null;
    } else if (expectedValue instanceof final ArrayNode expectedArrayNode && actualValue instanceof final ArrayNode actualArrayNode) {
      // If both values are arrays, compare each of their elements. Order should be preserved
      return IntStream.range(0, expectedArrayNode.size())
          .allMatch(i -> areJsonNodesEquivalent(expectedArrayNode.get(i), actualArrayNode.get(i)));
    } else if (expectedValue instanceof final ObjectNode expectedObjectNode && actualValue instanceof final ObjectNode actualObjectNode) {
      // If both values are objects compare their fields and values
      return expectedObjectNode.size() == actualObjectNode.size() && Stream.generate(expectedObjectNode.fieldNames()::next)
          .limit(expectedObjectNode.size())
          .allMatch(field -> areJsonNodesEquivalent(expectedObjectNode.get(field), actualObjectNode.get(field)));
    } else {
      // Otherwise, we need to compare the actual values.
      // This is kind of sketchy, but seems to work fine for the data we have in our test cases.
      return expectedValue.equals(actualValue)
          // equals() expects the two values to be the same class.
          // We need to handle comparisons between e.g. LongNode and IntNode.
          || (expectedValue.isIntegralNumber() && actualValue.isIntegralNumber()
              && expectedValue.bigIntegerValue().equals(actualValue.bigIntegerValue()))
          || (expectedValue.isNumber() && actualValue.isNumber() && expectedValue.decimalValue().equals(actualValue.decimalValue()));
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
  private LinkedHashMap<String, JsonNode> checkForExtraOrNonNullFields(final JsonNode expectedRecord,
                                                                       final JsonNode actualRecord,
                                                                       final Map<String, String> columnNames) {
    final LinkedHashMap<String, JsonNode> extraFields = new LinkedHashMap<>();
    for (final String column : Streams.stream(actualRecord.fieldNames()).sorted().toList()) {
      // loaded_at and raw_id are generated dynamically, so we just ignore them.
      final boolean isLoadedAt = getMetadataColumnName(columnNames, "_airbyte_loaded_at").equals(column);
      final boolean isRawId = getMetadataColumnName(columnNames, "_airbyte_raw_id").equals(column);
      final boolean isExpected = expectedRecord.has(column);
      if (!(isLoadedAt || isRawId || isExpected)) {
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
  private static String generateFieldError(final String fieldname, final JsonNode expectedValue, final JsonNode actualValue) {
    final String expectedString = expectedValue == null ? "SQL NULL (i.e. no value)" : expectedValue.toString();
    final String actualString = actualValue == null ? "SQL NULL (i.e. no value)" : actualValue.toString();
    return "  For " + fieldname + ", expected " + expectedString + " but got " + actualString + "\n";
  }

  // These asFoo methods are used for sorting records, so their defaults are intended to make broken
  // records stand out.
  private static String asString(final JsonNode node) {
    if (node == null || node.isNull()) {
      return "";
    } else if (node.isTextual()) {
      return node.asText();
    } else {
      return Jsons.serialize(node);
    }
  }

  private static BigDecimal asNumber(final JsonNode node) {
    if (node == null || !node.isNumber()) {
      return new BigDecimal(Double.MIN_VALUE);
    } else {
      return node.decimalValue();
    }
  }

  private static long asInt(final JsonNode node) {
    if (node == null || !node.isIntegralNumber()) {
      return Long.MIN_VALUE;
    } else {
      return node.longValue();
    }
  }

  private static boolean asBoolean(final JsonNode node) {
    if (node == null || !node.isBoolean()) {
      return false;
    } else {
      return node.asBoolean();
    }
  }

  private static Instant asTimestampWithTimezone(final JsonNode node) {
    if (node == null || !node.isTextual()) {
      return Instant.ofEpochMilli(Long.MIN_VALUE);
    } else {
      try {
        return Instant.parse(node.asText());
      } catch (final Exception e) {
        return Instant.ofEpochMilli(Long.MIN_VALUE);
      }
    }
  }

  private static LocalDateTime asTimestampWithoutTimezone(final JsonNode node) {
    if (node == null || !node.isTextual()) {
      return LocalDateTime.ofInstant(Instant.ofEpochMilli(Long.MIN_VALUE), ZoneOffset.UTC);
    } else {
      try {
        return LocalDateTime.parse(node.asText());
      } catch (final Exception e) {
        return LocalDateTime.ofInstant(Instant.ofEpochMilli(Long.MIN_VALUE), ZoneOffset.UTC);
      }
    }
  }

  private static OffsetTime asTimeWithTimezone(final JsonNode node) {
    if (node == null || !node.isTextual()) {
      return OffsetTime.of(0, 0, 0, 0, ZoneOffset.UTC);
    } else {
      return OffsetTime.parse(node.asText());
    }
  }

  private static LocalTime asTimeWithoutTimezone(final JsonNode node) {
    if (node == null || !node.isTextual()) {
      return LocalTime.of(0, 0, 0);
    } else {
      try {
        return LocalTime.parse(node.asText());
      } catch (final Exception e) {
        return LocalTime.of(0, 0, 0);
      }
    }
  }

  private static LocalDate asDate(final JsonNode node) {
    if (node == null || !node.isTextual()) {
      return LocalDate.ofInstant(Instant.ofEpochMilli(Long.MIN_VALUE), ZoneOffset.UTC);
    } else {
      try {
        return LocalDate.parse(node.asText());
      } catch (final Exception e) {
        return LocalDate.ofInstant(Instant.ofEpochMilli(Long.MIN_VALUE), ZoneOffset.UTC);
      }
    }
  }

  // Generics? Never heard of 'em. (I'm sorry)
  private static Comparable extract(final JsonNode node, final String field, final AirbyteType type) {
    if (type instanceof final AirbyteProtocolType t) {
      return switch (t) {
        case STRING -> asString(node.get(field));
        case NUMBER -> asNumber(node.get(field));
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

  private String getMetadataColumnName(final Map<String, String> columnNames, final String columnName) {
    return columnNames.getOrDefault(columnName, columnName);
  }

}
