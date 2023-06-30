/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Streams;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.configoss.WorkerDestinationConfig;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import io.airbyte.workers.internal.AirbyteDestination;
import io.airbyte.workers.internal.DefaultAirbyteDestination;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.Collections;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Function;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This is loosely based on standard-destination-tests's DestinationAcceptanceTest class. The
 * sync-running code is copy-pasted from there.
 * <p>
 * All tests use a single stream, whose schema is defined in {@code resources/schema.json}. Each
 * test case constructs a ConfiguredAirbyteCatalog dynamically.
 * <p>
 * For sync modes which use a primary key, the stream provides a composite key of (id1, id2). For
 * sync modes which use a cursor, the stream provides an updated_at field. The stream also has an
 * _ab_cdc_deleted_at field.
 */
// Remember to set `'junit.jupiter.execution.parallel.enabled': 'true'` in your connector's
// build.gradle.
// See destination-bigquery for an example.
// If you're running from inside intellij, you must run your specific subclass to get concurrent
// execution.
@Execution(ExecutionMode.CONCURRENT)
public abstract class BaseTypingDedupingTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseTypingDedupingTest.class);
  private static final Comparator<JsonNode> RAW_RECORD_IDENTITY_COMPARATOR = Comparator
      .comparingLong((JsonNode record) -> asInt(record.get("_airbyte_data").get("id1")))
      .thenComparingLong(record -> asInt(record.get("_airbyte_data").get("id2")))
      .thenComparing(record -> asTimestamp(record.get("_airbyte_data").get("updated_at")))
      .thenComparing(record -> asTimestamp(record.get("_airbyte_extracted_at")));
  private static final Comparator<JsonNode> RAW_RECORD_SORT_COMPARATOR = RAW_RECORD_IDENTITY_COMPARATOR
      .thenComparing(record -> asString(record.get("_airbyte_raw_id")));
  private static final Comparator<JsonNode> FINAL_RECORD_IDENTITY_COMPARATOR = Comparator
      .comparingLong((JsonNode record) -> asInt(record.get("id1")))
      .thenComparingLong(record -> asInt(record.get("id2")))
      .thenComparing(record -> asTimestamp(record.get("updated_at")))
      .thenComparing(record -> asTimestamp(record.get("_airbyte_extracted_at")));
  private static final Comparator<JsonNode> FINAL_RECORD_SORT_COMPARATOR = FINAL_RECORD_IDENTITY_COMPARATOR
      .thenComparing(record -> asString(record.get("_airbyte_raw_id")));

  private String randomSuffix;
  private JsonNode config;
  private String streamNamespace;
  private String streamName;

  /**
   * @return the docker image to run, e.g. {@code "airbyte/destination-bigquery:dev"}.
   */
  protected abstract String getImageName();

  /**
   * Get the destination connector config. Subclasses may use this method for other setup work, e.g.
   * opening a connection to the destination.
   * <p>
   * Subclasses should _not_ start testcontainers in this method; that belongs in a BeforeAll method.
   * The tests in this class are intended to be run concurrently on a shared database and will not
   * interfere with each other.
   */
  protected abstract JsonNode generateConfig() throws Exception;

  /**
   * For a given stream, return the records that exist in the destination's raw table. Each record
   * must be in the format {"_airbyte_raw_id": "...", "_airbyte_extracted_at": "...",
   * "_airbyte_loaded_at": "...", "_airbyte_data": {fields...}}.
   * <p>
   * The {@code _airbyte_data} column must be an
   * {@link com.fasterxml.jackson.databind.node.ObjectNode} (i.e. it cannot be a string value).
   * <p>
   * streamNamespace may be null, in which case you should query from the default namespace.
   */
  protected abstract List<JsonNode> dumpRawTableRecords(String streamNamespace, String streamName) throws Exception;

  /**
   * For a given stream, return the records that exist in the destination's final table. Each record
   * must be in the format {"_airbyte_raw_id": "...", "_airbyte_extracted_at": "...", "_airbyte_meta":
   * {...}, "field1": ..., "field2": ..., ...}.
   * <p>
   * For JSON-valued columns, there is some nuance: a SQL null should be represented as a missing
   * entry, whereas a JSON null should be represented as a
   * {@link com.fasterxml.jackson.databind.node.NullNode}. For example, in the JSON blob {"name":
   * null}, the `name` field is a JSON null, and the `address` field is a SQL null.
   * <p>
   * The corresponding SQL looks like
   * {@code INSERT INTO ... (name, address) VALUES ('null' :: jsonb, NULL)}.
   * <p>
   * streamNamespace may be null, in which case you should query from the default namespace.
   */
  protected abstract List<JsonNode> dumpFinalTableRecords(String streamNamespace, String streamName) throws Exception;

  /**
   * Delete any resources in the destination associated with this stream AND its namespace. We need
   * this because we write raw tables to a shared {@code airbyte} namespace, which we can't drop
   * wholesale.
   * <p>
   * In general, this should resemble
   * {@code DROP TABLE IF EXISTS airbyte.namespace_name; DROP SCHEMA IF EXISTS namespace}.
   */
  protected abstract void teardownStreamAndNamespace(String streamNamespace, String streamName) throws Exception;

  /**
   * @return A suffix which is different for each concurrent test run.
   */
  protected synchronized String getUniqueSuffix() {
    if (randomSuffix == null) {
      randomSuffix = "_" + RandomStringUtils.randomAlphabetic(5).toLowerCase();
    }
    return randomSuffix;
  }

  protected JsonNode getConfig() {
    return config;
  }

  @BeforeEach
  public void setup() throws Exception {
    config = generateConfig();
    streamNamespace = "typing_deduping_test" + getUniqueSuffix();
    streamName = "test_stream" + getUniqueSuffix();
    LOGGER.info("Using stream namespace {} and name {}", streamNamespace, streamName);
  }

  @AfterEach
  public void teardown() throws Exception {
    teardownStreamAndNamespace(streamNamespace, streamName);
  }

  /**
   * Starting with an empty destination, execute a full refresh overwrite sync. Verify that the
   * records are written to the destination table. Then run a second sync, and verify that the records
   * are overwritten.
   */
  @Test
  public void fullRefreshOverwrite() throws Exception {
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(getSchema()))));

    // First sync
    List<AirbyteMessage> messages1 = readMessages("sync1_messages.jsonl");

    runSync(catalog, messages1);

    List<JsonNode> expectedRawRecords1 = readRecords("sync1_expectedrecords_nondedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords1 = readRecords("sync1_expectedrecords_nondedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1);

    // Second sync
    List<AirbyteMessage> messages2 = readMessages("sync2_messages.jsonl");

    runSync(catalog, messages2);

    List<JsonNode> expectedRawRecords2 = readRecords("sync2_expectedrecords_fullrefresh_overwrite_raw.jsonl");
    List<JsonNode> expectedFinalRecords2 = readRecords("sync2_expectedrecords_fullrefresh_overwrite_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2);
  }

  /**
   * Starting with an empty destination, execute a full refresh append sync. Verify that the records
   * are written to the destination table. Then run a second sync, and verify that the old and new
   * records are all present.
   */
  @Test
  public void fullRefreshAppend() throws Exception {
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(getSchema()))));

    // First sync
    List<AirbyteMessage> messages1 = readMessages("sync1_messages.jsonl");

    runSync(catalog, messages1);

    List<JsonNode> expectedRawRecords1 = readRecords("sync1_expectedrecords_nondedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords1 = readRecords("sync1_expectedrecords_nondedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1);

    // Second sync
    List<AirbyteMessage> messages2 = readMessages("sync2_messages.jsonl");

    runSync(catalog, messages2);

    List<JsonNode> expectedRawRecords2 = readRecords("sync2_expectedrecords_fullrefresh_append_raw.jsonl");
    List<JsonNode> expectedFinalRecords2 = readRecords("sync2_expectedrecords_fullrefresh_append_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2);
  }

  /**
   * Starting with an empty destination, execute an incremental append sync.
   * <p>
   * This is (not so secretly) identical to {@link #fullRefreshAppend()}, and uses the same set of
   * expected records. Incremental as a concept only exists in the source. From the destination's
   * perspective, we only care about the destination sync mode.
   */
  @Test
  public void incrementalAppend() throws Exception {
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            // These two lines are literally the only difference between this test and fullRefreshAppend
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(getSchema()))));

    // First sync
    List<AirbyteMessage> messages1 = readMessages("sync1_messages.jsonl");

    runSync(catalog, messages1);

    List<JsonNode> expectedRawRecords1 = readRecords("sync1_expectedrecords_nondedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords1 = readRecords("sync1_expectedrecords_nondedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1);

    // Second sync
    List<AirbyteMessage> messages2 = readMessages("sync2_messages.jsonl");

    runSync(catalog, messages2);

    List<JsonNode> expectedRawRecords2 = readRecords("sync2_expectedrecords_fullrefresh_append_raw.jsonl");
    List<JsonNode> expectedFinalRecords2 = readRecords("sync2_expectedrecords_fullrefresh_append_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2);
  }

  /**
   * Starting with an empty destination, execute an incremental dedup sync. Verify that the records
   * are written to the destination table. Then run a second sync, and verify that the raw/final
   * tables contain the correct records.
   */
  @Test
  public void incrementalDedup() throws Exception {
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(getSchema()))));

    // First sync
    List<AirbyteMessage> messages1 = readMessages("sync1_messages.jsonl");

    runSync(catalog, messages1);

    List<JsonNode> expectedRawRecords1 = readRecords("sync1_expectedrecords_dedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords1 = readRecords("sync1_expectedrecords_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1);

    // Second sync
    List<AirbyteMessage> messages2 = readMessages("sync2_messages.jsonl");

    runSync(catalog, messages2);

    List<JsonNode> expectedRawRecords2 = readRecords("sync2_expectedrecords_incremental_dedup_raw.jsonl");
    List<JsonNode> expectedFinalRecords2 = readRecords("sync2_expectedrecords_incremental_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2);
  }

  @Test
  @Disabled("Not yet implemented")
  public void testLineBreakCharacters() throws Exception {
    // TODO verify that we can handle strings with interesting characters
    // build an airbyterecordmessage using something like this, and add it to the input messages:
    Jsons.jsonNode(ImmutableMap.builder()
        .put("id", 1)
        .put("currency", "USD\u2028")
        .put("date", "2020-03-\n31T00:00:00Z\r")
        // TODO(sherifnada) hack: write decimals with sigfigs because Snowflake stores 10.1 as "10" which
        // fails destination tests
        .put("HKD", 10.1)
        .put("NZD", 700.1)
        .build());
  }

  @Test
  @Disabled("Not yet implemented")
  public void testIncrementalSyncDropOneColumn() throws Exception {
    // TODO in incremental dedup mode: run a sync, remove a column from the schema, run another sync
    // verify that the column is dropped from the destination table
  }

  @Test
  @Disabled("Not yet implemented")
  public void testSyncUsesAirbyteStreamNamespaceIfNotNull() throws Exception {
    // TODO duplicate this test for each sync mode. Run 1st+2nd syncs using a stream with null
    // namespace:
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(null)
                .withName(streamName)
                .withJsonSchema(getSchema()))));
  }

  @Test
  @Disabled("Not yet implemented")
  public void testSyncWriteSameTableNameDifferentNamespace() throws Exception {
    // TODO duplicate this test for each sync mode. Run 1st+2nd syncs using two streams with the same
    // name but different namespace:
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace + "_1")
                .withName(streamName)
                .withJsonSchema(getSchema())),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace + "_2")
                .withName(streamName)
                .withJsonSchema(getSchema()))));
  }

  @Test
  @Disabled("Not yet implemented")
  public void testSyncNotFailsWithNewFields() throws Exception {
    // TODO duplicate this test for each sync mode. Run a sync, then add a new field to the schema, then
    // run another sync
    // We might want to write a test that verifies more general schema evolution (e.g. all valid
    // evolutions)
  }

  @Test
  @Disabled("Not yet implemented")
  public void testSyncWithLargeRecordBatch() throws Exception {
    // TODO duplicate this test for each sync mode. Run a single sync with many records
    /*
     * copied from DATs: This serves to test MSSQL 2100 limit parameters in a single query. this means
     * that for Airbyte insert data need to limit to ~ 700 records (3 columns for the raw tables) = 2100
     * params
     *
     * this maybe needs configuration per destination to specify that limit?
     */
  }

  @Test
  @Disabled("Not yet implemented")
  public void testDataTypes() throws Exception {
    // TODO duplicate this test for each sync mode. See DataTypeTestArgumentProvider for what this test
    // does in DAT-land
    // we probably don't want to do the exact same thing, but the general spirit of testing a wide range
    // of values for every data type is approximately correct
    // this test probably needs some configuration per destination to specify what values are supported?
  }

  private static JsonNode getSchema() throws IOException {
    return Jsons.deserialize(MoreResources.readResource("schema.json"));
  }

  private List<JsonNode> readRecords(String filename) throws IOException {
    return MoreResources.readResource(filename).lines()
        .map(String::trim)
        .filter(line -> !line.isEmpty())
        .filter(line -> !line.startsWith("//"))
        .map(Jsons::deserialize)
        .toList();
  }

  private List<AirbyteMessage> readMessages(String filename) throws IOException {
    return readRecords(filename).stream()
        .map(record -> Jsons.convertValue(record, AirbyteMessage.class))
        .peek(message -> {
          message.getRecord().setNamespace(streamNamespace);
          message.getRecord().setStream(streamName);
        }).toList();
  }

  private void verifySyncResult(List<JsonNode> expectedRawRecords, List<JsonNode> expectedFinalRecords) throws Exception {
    List<JsonNode> actualRawRecords = dumpRawTableRecords(streamNamespace, streamName);
    String rawDiff = diffRawTableRecords(expectedRawRecords, actualRawRecords);
    List<JsonNode> actualFinalRecords = dumpFinalTableRecords(streamNamespace, streamName);
    String finalDiff = diffFinalTableRecords(expectedFinalRecords, actualFinalRecords);

    assertAll(
        () -> assertTrue(rawDiff.isEmpty(), "Raw table was incorrect.\n" + rawDiff),
        () -> assertTrue(finalDiff.isEmpty(), "Final table was incorrect.\n" + finalDiff));
  }

  private static String diffRawTableRecords(List<JsonNode> expectedRecords, List<JsonNode> actualRecords) {
    return diffRecords(
        expectedRecords,
        actualRecords,
        RAW_RECORD_IDENTITY_COMPARATOR,
        RAW_RECORD_SORT_COMPARATOR,
        record -> getFieldIfPresent(record.get("_airbyte_data"), "id1")
            + getFieldIfPresent(record.get("_airbyte_data"), "id2")
            + getFieldIfPresent(record.get("_airbyte_data"), "updated_at")
            + getFieldIfPresent(record, "_airbyte_extracted_at"),
        true);
  }

  private static String diffFinalTableRecords(List<JsonNode> expectedRecords, List<JsonNode> actualRecords) {
    return diffRecords(
        expectedRecords,
        actualRecords,
        FINAL_RECORD_IDENTITY_COMPARATOR,
        FINAL_RECORD_SORT_COMPARATOR,
        record -> getFieldIfPresent(record, "id1")
            + getFieldIfPresent(record, "id2")
            + getFieldIfPresent(record, "updated_at")
            + getFieldIfPresent(record, "_airbyte_extracted_at"),
        false);
  }

  private static String getFieldIfPresent(JsonNode record, String field) {
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
   * {@link #dumpFinalTableRecords(String, String)} for an explanation of how SQL/JSON nulls are
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
   * Produce a pretty-printed error message, e.g. " For column foo, expected 1 but got 2". It's
   * indented intentionally.
   */
  private static String generateFieldError(String fieldname, JsonNode expectedValue, JsonNode actualValue) {
    String expectedString = expectedValue == null ? "SQL NULL (i.e. no value)" : expectedValue.toString();
    String actualString = actualValue == null ? "SQL NULL (i.e. no value)" : actualValue.toString();
    return "  For " + fieldname + ", expected " + expectedString + " but got " + actualString + "\n";
  }

  // These asFoo methods are used for sorting records, so their defaults are intended to make broken
  // records stand out.
  private static long asInt(JsonNode node) {
    if (node == null || !node.isIntegralNumber()) {
      return Long.MIN_VALUE;
    } else {
      return node.longValue();
    }
  }

  private static String asString(JsonNode node) {
    if (node == null || node.isNull()) {
      return "";
    } else if (node.isTextual()) {
      return node.asText();
    } else {
      return Jsons.serialize(node);
    }
  }

  private static Instant asTimestamp(JsonNode node) {
    if (node == null || !node.isTextual()) {
      return Instant.ofEpochMilli(Long.MIN_VALUE);
    } else {
      return Instant.parse(node.asText());
    }
  }

  /*
   * !!!!!! WARNING !!!!!! The code below was mostly copypasted from DestinationAcceptanceTest. If you
   * make edits here, you probably want to also edit there.
   */

  // These contain some state, so they are instanced per test (i.e. cannot be static)
  private Path jobRoot;
  private ProcessFactory processFactory;

  @BeforeEach
  public void setupProcessFactory() throws IOException {
    final Path testDir = Path.of("/tmp/airbyte_tests/");
    Files.createDirectories(testDir);
    final Path workspaceRoot = Files.createTempDirectory(testDir, "test");
    jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"));
    Path localRoot = Files.createTempDirectory(testDir, "output");
    processFactory = new DockerProcessFactory(
        workspaceRoot,
        workspaceRoot.toString(),
        localRoot.toString(),
        "host",
        Collections.emptyMap());
  }

  private void runSync(ConfiguredAirbyteCatalog catalog, List<AirbyteMessage> messages) throws Exception {
    final WorkerDestinationConfig destinationConfig = new WorkerDestinationConfig()
        .withConnectionId(UUID.randomUUID())
        .withCatalog(convertProtocolObject(catalog, io.airbyte.protocol.models.ConfiguredAirbyteCatalog.class))
        .withDestinationConnectionConfiguration(config);

    final AirbyteDestination destination = new DefaultAirbyteDestination(new AirbyteIntegrationLauncher(
        "0",
        0,
        getImageName(),
        processFactory,
        null,
        null,
        false,
        new EnvVariableFeatureFlags()));

    destination.start(destinationConfig, jobRoot, Collections.emptyMap());
    messages.forEach(
        message -> Exceptions.toRuntime(() -> destination.accept(convertProtocolObject(message, io.airbyte.protocol.models.AirbyteMessage.class))));
    destination.notifyEndOfInput();

    while (!destination.isFinished()) {
      destination.attemptRead();
    }

    destination.close();
  }

  private static <V0, V1> V0 convertProtocolObject(final V1 v1, final Class<V0> klass) {
    return Jsons.object(Jsons.jsonNode(v1), klass);
  }

}
