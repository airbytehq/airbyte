package io.airbyte.integrations.base.destination.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Streams;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
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
import java.util.List;
import java.util.Objects;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This is loosely based on standard-destination-tests's DestinationAcceptanceTest class. The sync-running code is copy-pasted from there.
 * <p>
 * All tests use a single stream, whose schema is defined in {@code resources/schema.json}. Each test case constructs a
 * ConfiguredAirbyteCatalog dynamically.
 * <p>
 * For sync modes which use a primary key, the stream provides a composite key of (id1, id2). For sync modes which use a
 * cursor, the stream provides an updated_at field. The stream also has an _ab_cdc_deleted_at field.
 */
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
  private static ProcessFactory processFactory;

  /**
   * Subclasses MUST implement a static {@link org.junit.jupiter.api.BeforeAll} method that sets this field.
   * <p>
   * That method should also start testcontainer(s), if you're using them. That test container will be used for all
   * tests. This is safe because each test uses a randomized stream namespace+name.
   */
  protected static JsonNode config;

  private String streamNamespace;
  private String streamName;

  /**
   * @return the docker image to run, e.g. {@code "airbyte/destination-bigquery:dev"}.
   */
  protected abstract String getImageName();

  /**
   * For a given stream, return the records that exist in the destination's raw table. This _should_ include metadata columns (e.g. _airbyte_raw_id).
   * The {@code _airbyte_data} column MUST be an {@link com.fasterxml.jackson.databind.node.ObjectNode} (i.e. it cannot be a string value).
   */
  protected abstract List<JsonNode> dumpRawTableRecords(String streamNamespace, String streamName) throws Exception;

  /**
   * For a given stream, return the records that exist in the destination's final table. This _should_ include metadata columns (e.g. _airbyte_raw_id).
   */
  protected abstract List<JsonNode> dumpFinalTableRecords(String streamNamespace, String streamName) throws Exception;

  /**
   * Create raw+final tables in the destinations as though a previous sync had loaded {@code initialRecords}. This method
   * exists so that we don't need to run a sync just to load initial state, because that's both slow and error-prone.
   */
  protected abstract void loadInitialRecords(String streamNamespace, String streamName, List<JsonNode> initialRecords) throws Exception;

  /**
   * Delete any resources in the destination associated with this stream AND its namespace. We need this because we write
   * raw tables to a shared {@code airbyte} namespace, which we can't drop wholesale.
   * <p>
   * In general, this should resemble {@code DROP TABLE airbyte.namespace_name; DROP SCHEMA namespace}.
   */
  protected abstract void teardownStreamAndNamespace(String streamNamespace, String streamName) throws Exception;

  @BeforeEach
  public void setup() {
    streamNamespace = Strings.addRandomSuffix("typing_deduping_test_namespace", "_", 5);
    streamName = Strings.addRandomSuffix("test_stream", "_", 5);
    LOGGER.info("Using stream namespace {} and name {}", streamNamespace, streamName);
  }

  @AfterEach
  public void teardown() throws Exception {
    teardownStreamAndNamespace(streamNamespace, streamName);
  }

  /**
   * Starting with an empty destination, execute a full refresh overwrite sync. Verify that the records are written to
   * the destination table.
   */
  @Test
  public void initialFullRefreshOverwrite() throws Exception {
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(getSchema()))));
    List<AirbyteMessage> messages = readMessages("sync1_messages.jsonl");

    runSync(catalog, messages);

    List<JsonNode> expectedRawRecords = readRecords("sync1_expectedrecords_fullrefresh_overwrite_raw.jsonl");
    List<JsonNode> expectedFinalRecords = readRecords("sync1_expectedrecords_fullrefresh_overwrite_final.jsonl");
    verifySyncResult(expectedRawRecords, expectedFinalRecords);
  }

  private static JsonNode getSchema() throws IOException {
    return Jsons.deserialize(MoreResources.readResource("schema.json"));
  }

  private List<AirbyteMessage> readMessages(String filename) throws IOException {
    return MoreResources.readResource(filename).lines()
        .filter(line -> !line.startsWith("//"))
        .map(jsonString -> Jsons.deserialize(jsonString, AirbyteMessage.class))
        .peek(message -> {
          message.getRecord().setNamespace(streamNamespace);
          message.getRecord().setStream(streamName);
        }).toList();
  }

  private List<JsonNode> readRecords(String filename) throws IOException {
    return MoreResources.readResource(filename).lines()
        .filter(line -> !line.startsWith("//"))
        .map(Jsons::deserialize)
        .toList();
  }

  private void verifySyncResult(List<JsonNode> expectedRawRecords, List<JsonNode> expectedFinalRecords) throws Exception {
    List<JsonNode> actualRawRecords = dumpRawTableRecords(streamNamespace, streamName);
    String rawDiff = diffRawTableRecords(expectedRawRecords, actualRawRecords);
    List<JsonNode> actualFinalRecords = dumpFinalTableRecords(streamNamespace, streamName);
    String finalDiff = diffFinalTableRecords(expectedFinalRecords, actualFinalRecords);

    assertAll(
        () -> assertTrue(rawDiff.isEmpty(), "Raw table was incorrect.\n" + rawDiff),
        () -> assertTrue(finalDiff.isEmpty(), "Final table was incorrect.\n" + finalDiff)
    );
  }

  private static String diffRawTableRecords(List<JsonNode> expectedRecords, List<JsonNode> actualRecords) {
    return diffRecords(expectedRecords, actualRecords, RAW_RECORD_IDENTITY_COMPARATOR, RAW_RECORD_SORT_COMPARATOR);
  }

  private static String diffFinalTableRecords(List<JsonNode> expectedRecords, List<JsonNode> actualRecords) {
    return diffRecords(expectedRecords, actualRecords, FINAL_RECORD_IDENTITY_COMPARATOR, FINAL_RECORD_SORT_COMPARATOR);
  }

  /**
   * Generate a human-readable diff between the two lists. Only checks the keys specified in expectedRecords.
   *
   * @param identityComparator Returns 0 iff two records are the "same" record (i.e. have the same PK+cursor+extracted_at)
   * @param sortComparator Behaves identically to identityComparator, but if two records are the same, breaks that tie using _airbyte_raw_id
   * @return The diff, or empty string if there were no differences
   */
  private static String diffRecords(
      List<JsonNode> originalExpectedRecords,
      List<JsonNode> originalActualRecords,
      Comparator<JsonNode> identityComparator, Comparator<JsonNode> sortComparator) {
    List<JsonNode> expectedRecords = originalExpectedRecords.stream().sorted(sortComparator).toList();
    List<JsonNode> actualRecords = originalActualRecords.stream().sorted(sortComparator).toList();

    // Iterate through both lists in parallel and compare each record.
    // Build up an error message listing any incorrect, missing, or unexpected records.
    // Not a true diff, but close enough.
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
        String mismatchedRecordMessage = "Row had incorrect data:\n";
        for (String key : Streams.stream(expectedRecord.fieldNames()).sorted().toList()) {
          JsonNode expectedValue = expectedRecord.get(key);
          JsonNode actualValue = actualRecord.get(key);
          // This is kind of sketchy, but seems to work fine for the data we have in our test cases.
          if (!Objects.equals(expectedValue, actualValue)
              // Objects.equals expects the two values to be the same class.
              // We need to handle comparisons between e.g. LongNode and IntNode.
              && !(expectedValue.isIntegralNumber() && actualValue.isIntegralNumber() && expectedValue.asLong() == actualValue.asLong())
              && !(expectedValue.isNumber() && actualValue.isNumber() && expectedValue.asDouble() == actualValue.asDouble())) {
            mismatchedRecordMessage += "  For key " + key + ", expected " + expectedValue + " but got " + actualValue + "\n";
            foundMismatch = true;
          }
        }
        if (foundMismatch) {
          message += mismatchedRecordMessage;
        }

        expectedRecordIndex++;
        actualRecordIndex++;
      } else if (compare < 0) {
        // The expected record is missing from the actual records. Print it and move on to the next expected record.
        message += "Row was expected but missing: " + expectedRecord + "\n";
        expectedRecordIndex++;
      } else {
        // There's an actual record which isn't present in the expected records. Print it and move on to the next actual record.
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

  private static long asInt(JsonNode node) {
    if (node == null || !node.isIntegralNumber()) {
      return Integer.MIN_VALUE;
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

  /* !!!!!! WARNING !!!!!!
   * The code below was mostly copypasted from DestinationAcceptanceTest. If you make edits here, you probably want to also edit there.
   * !!!!!!!!!!!!!!!!!!!!!
   */

  private static Path jobRoot;

  @BeforeAll
  public static void globalSetup() throws IOException {
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
    messages.forEach(message -> Exceptions.toRuntime(() ->
        destination.accept(convertProtocolObject(message, io.airbyte.protocol.models.AirbyteMessage.class))));
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
