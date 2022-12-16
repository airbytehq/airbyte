/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source;

import static io.airbyte.protocol.models.v0.SyncMode.FULL_REFRESH;
import static io.airbyte.protocol.models.v0.SyncMode.INCREMENTAL;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Iterables;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class SourceAcceptanceTest extends AbstractSourceConnectorTest {

  public static final String CDC_LSN = "_ab_cdc_lsn";
  public static final String CDC_UPDATED_AT = "_ab_cdc_updated_at";
  public static final String CDC_DELETED_AT = "_ab_cdc_deleted_at";
  public static final String CDC_LOG_FILE = "_ab_cdc_log_file";
  public static final String CDC_LOG_POS = "_ab_cdc_log_pos";

  private static final Logger LOGGER = LoggerFactory.getLogger(SourceAcceptanceTest.class);

  /**
   * TODO hack: Various Singer integrations use cursor fields inclusively i.e: they output records
   * whose cursor field >= the provided cursor value. This leads to the last record in a sync to
   * always be the first record in the next sync. This is a fine assumption from a product POV since
   * we offer at-least-once delivery. But for simplicity, the incremental test suite currently assumes
   * that the second incremental read should output no records when provided the state from the first
   * sync. This works for many integrations but not some Singer ones, so we hardcode the list of
   * integrations to skip over when performing those tests.
   */
  private final Set<String> IMAGES_TO_SKIP_SECOND_INCREMENTAL_READ = Sets.newHashSet(
      "airbyte/source-intercom-singer",
      "airbyte/source-exchangeratesapi-singer",
      "airbyte/source-hubspot",
      "airbyte/source-iterable",
      "airbyte/source-marketo-singer",
      "airbyte/source-twilio-singer",
      "airbyte/source-mixpanel-singer",
      "airbyte/source-twilio-singer",
      "airbyte/source-braintree-singer",
      "airbyte/source-stripe-singer",
      "airbyte/source-exchange-rates",
      "airbyte/source-stripe",
      "airbyte/source-github-singer",
      "airbyte/source-gitlab-singer",
      "airbyte/source-google-workspace-admin-reports",
      "airbyte/source-zendesk-talk",
      "airbyte/source-zendesk-support-singer",
      "airbyte/source-quickbooks-singer",
      "airbyte/source-jira");

  /**
   * FIXME: Some sources can't guarantee that there will be no events between two sequential sync
   */
  private final Set<String> IMAGES_TO_SKIP_IDENTICAL_FULL_REFRESHES = Sets.newHashSet(
      "airbyte/source-google-workspace-admin-reports", "airbyte/source-kafka");

  /**
   * Specification for integration. Will be passed to integration where appropriate in each test.
   * Should be valid.
   *
   * @return integration-specific configuration
   */
  protected abstract ConnectorSpecification getSpec() throws Exception;

  /**
   * The catalog to use to validate the output of read operations. This will be used as follows:
   * <p>
   * Full Refresh syncs will be tested on all the input streams which support it Incremental syncs: -
   * if the stream declares a source-defined cursor, it will be tested with an incremental sync using
   * the default cursor. - if the stream requires a user-defined cursor, it will be tested with the
   * input cursor in both cases, the input {@link #getState()} will be used as the input state.
   *
   * @return
   * @throws Exception
   */
  protected abstract ConfiguredAirbyteCatalog getConfiguredCatalog() throws Exception;

  /**
   * @return a JSON file representing the state file to use when testing incremental syncs
   */
  protected abstract JsonNode getState() throws Exception;

  /**
   * Tests whether the connector under test supports the per-stream state format or should use the
   * legacy format for data generated by this test.
   *
   * @return {@code true} if the connector supports the per-stream state format or {@code false} if it
   *         does not support the per-stream state format (e.g. legacy format supported). Default
   *         value is {@code false}.
   */
  protected boolean supportsPerStream() {
    return false;
  }

  /**
   * Verify that a spec operation issued to the connector returns a valid spec.
   */
  @Test
  public void testGetSpec() throws Exception {
    assertEquals(getSpec(), runSpec(), "Expected spec output by integration to be equal to spec provided by test runner");
  }

  /**
   * Verify that a check operation issued to the connector with the input config file returns a
   * success response.
   */
  @Test
  public void testCheckConnection() throws Exception {
    assertEquals(Status.SUCCEEDED, runCheck().getStatus(), "Expected check connection operation to succeed");
  }

  // /**
  // * Verify that when given invalid credentials, that check connection returns a failed response.
  // * Assume that the {@link TestSource#getFailCheckConfig()} is invalid.
  // */
  // @Test
  // public void testCheckConnectionInvalidCredentials() throws Exception {
  // final OutputAndStatus<StandardCheckConnectionOutput> output = runCheck();
  // assertTrue(output.getOutput().isPresent());
  // assertEquals(Status.FAILED, output.getOutput().get().getStatus());
  // }

  /**
   * Verifies when a discover operation is run on the connector using the given config file, a valid
   * catalog is output by the connector.
   */
  @Test
  public void testDiscover() throws Exception {
    final UUID discoverOutput = runDiscover();
    final AirbyteCatalog discoveredCatalog = getLastPersistedCatalog();
    assertNotNull(discoveredCatalog, "Expected discover to produce a catalog");
    verifyCatalog(discoveredCatalog);
  }

  /**
   * Override this method to check the actual catalog.
   */
  protected void verifyCatalog(final AirbyteCatalog catalog) throws Exception {
    // do nothing by default
  }

  /**
   * Configuring all streams in the input catalog to full refresh mode, verifies that a read operation
   * produces some RECORD messages.
   */
  @Test
  public void testFullRefreshRead() throws Exception {
    final ConfiguredAirbyteCatalog catalog = withFullRefreshSyncModes(getConfiguredCatalog());
    final List<AirbyteMessage> allMessages = runRead(catalog);

    assertFalse(filterRecords(allMessages).isEmpty(), "Expected a full refresh sync to produce records");
    assertFullRefreshMessages(allMessages);
  }

  /**
   * Override this method to perform more specific assertion on the messages.
   */
  protected void assertFullRefreshMessages(final List<AirbyteMessage> allMessages) throws Exception {
    // do nothing by default
  }

  /**
   * Configuring all streams in the input catalog to full refresh mode, performs two read operations
   * on all streams which support full refresh syncs. It then verifies that the RECORD messages output
   * from both were identical.
   */
  @Test
  public void testIdenticalFullRefreshes() throws Exception {
    if (IMAGES_TO_SKIP_IDENTICAL_FULL_REFRESHES.contains(getImageName().split(":")[0])) {
      return;
    }

    final ConfiguredAirbyteCatalog configuredCatalog = withFullRefreshSyncModes(getConfiguredCatalog());
    final List<AirbyteRecordMessage> recordMessagesFirstRun = filterRecords(runRead(configuredCatalog));
    final List<AirbyteRecordMessage> recordMessagesSecondRun = filterRecords(runRead(configuredCatalog));
    // the worker validates the messages, so we just validate the message, so we do not need to validate
    // again (as long as we use the worker, which we will not want to do long term).
    assertFalse(recordMessagesFirstRun.isEmpty(), "Expected first full refresh to produce records");
    assertFalse(recordMessagesSecondRun.isEmpty(), "Expected second full refresh to produce records");

    assertSameRecords(recordMessagesFirstRun, recordMessagesSecondRun, "Expected two full refresh syncs to produce the same records");
  }

  /**
   * This test verifies that all streams in the input catalog which support incremental sync can do so
   * correctly. It does this by running two read operations on the connector's Docker image: the first
   * takes the configured catalog and config provided to this test as input. It then verifies that the
   * sync produced a non-zero number of RECORD and STATE messages.
   * <p>
   * The second read takes the same catalog and config used in the first test, plus the last STATE
   * message output by the first read operation as the input state file. It verifies that no records
   * are produced (since we read all records in the first sync).
   * <p>
   * This test is performed only for streams which support incremental. Streams which do not support
   * incremental sync are ignored. If no streams in the input catalog support incremental sync, this
   * test is skipped.
   */
  @Test
  public void testIncrementalSyncWithState() throws Exception {
    if (!sourceSupportsIncremental()) {
      return;
    }

    final ConfiguredAirbyteCatalog configuredCatalog = withSourceDefinedCursors(getConfiguredCatalog());
    // only sync incremental streams
    configuredCatalog.setStreams(
        configuredCatalog.getStreams().stream().filter(s -> s.getSyncMode() == INCREMENTAL).collect(Collectors.toList()));

    final List<AirbyteMessage> airbyteMessages = runRead(configuredCatalog, getState());
    final List<AirbyteRecordMessage> recordMessages = filterRecords(airbyteMessages);
    final List<AirbyteStateMessage> stateMessages = airbyteMessages
        .stream()
        .filter(m -> m.getType() == Type.STATE)
        .map(AirbyteMessage::getState)
        .collect(Collectors.toList());
    assertFalse(recordMessages.isEmpty(), "Expected the first incremental sync to produce records");
    assertFalse(stateMessages.isEmpty(), "Expected incremental sync to produce STATE messages");
    // TODO validate exact records

    if (IMAGES_TO_SKIP_SECOND_INCREMENTAL_READ.contains(getImageName().split(":")[0])) {
      return;
    }

    // when we run incremental sync again there should be no new records. Run a sync with the latest
    // state message and assert no records were emitted.
    final JsonNode latestState = Jsons.jsonNode(supportsPerStream() ? stateMessages : List.of(Iterables.getLast(stateMessages)));
    final List<AirbyteRecordMessage> secondSyncRecords = filterRecords(runRead(configuredCatalog, latestState));
    assertTrue(
        secondSyncRecords.isEmpty(),
        "Expected the second incremental sync to produce no records when given the first sync's output state.");
  }

  /**
   * If the source does not support incremental sync, this test is skipped.
   * <p>
   * Otherwise, this test runs two syncs: one where all streams provided in the input catalog sync in
   * full refresh mode, and another where all the streams which in the input catalog which support
   * incremental, sync in incremental mode (streams which don't support incremental sync in full
   * refresh mode). Then, the test asserts that the two syncs produced the same RECORD messages. Any
   * other type of message is disregarded.
   */
  @Test
  public void testEmptyStateIncrementalIdenticalToFullRefresh() throws Exception {
    if (!sourceSupportsIncremental()) {
      return;
    }

    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();
    final ConfiguredAirbyteCatalog fullRefreshCatalog = withFullRefreshSyncModes(configuredCatalog);

    final List<AirbyteRecordMessage> fullRefreshRecords = filterRecords(runRead(fullRefreshCatalog));
    final List<AirbyteRecordMessage> emptyStateRecords = filterRecords(runRead(configuredCatalog, Jsons.jsonNode(new HashMap<>())));
    final String assertionMessage = "Expected a full refresh sync and incremental sync with no input state to produce identical records";
    assertFalse(fullRefreshRecords.isEmpty(), assertionMessage);
    assertFalse(emptyStateRecords.isEmpty(), assertionMessage);
    assertSameRecords(fullRefreshRecords, emptyStateRecords, assertionMessage);
  }

  /**
   * In order to launch a source on Kubernetes in a pod, we need to be able to wrap the entrypoint.
   * The source connector must specify its entrypoint in the AIRBYTE_ENTRYPOINT variable. This test
   * ensures that the entrypoint environment variable is set.
   */
  @Test
  public void testEntrypointEnvVar() throws Exception {
    checkEntrypointEnvVariable();
  }

  protected static List<AirbyteRecordMessage> filterRecords(final Collection<AirbyteMessage> messages) {
    return messages.stream()
        .filter(m -> m.getType() == Type.RECORD)
        .map(AirbyteMessage::getRecord)
        .collect(Collectors.toList());
  }

  protected ConfiguredAirbyteCatalog withSourceDefinedCursors(final ConfiguredAirbyteCatalog catalog) {
    final ConfiguredAirbyteCatalog clone = Jsons.clone(catalog);
    for (final ConfiguredAirbyteStream configuredStream : clone.getStreams()) {
      if (configuredStream.getSyncMode() == INCREMENTAL
          && configuredStream.getStream().getSourceDefinedCursor() != null
          && configuredStream.getStream().getSourceDefinedCursor()) {
        configuredStream.setCursorField(configuredStream.getStream().getDefaultCursorField());
      }
    }
    return clone;
  }

  protected ConfiguredAirbyteCatalog withFullRefreshSyncModes(final ConfiguredAirbyteCatalog catalog) {
    final ConfiguredAirbyteCatalog clone = Jsons.clone(catalog);
    for (final ConfiguredAirbyteStream configuredStream : clone.getStreams()) {
      if (configuredStream.getStream().getSupportedSyncModes().contains(FULL_REFRESH)) {
        configuredStream.setSyncMode(FULL_REFRESH);
        configuredStream.setDestinationSyncMode(DestinationSyncMode.OVERWRITE);
      }
    }
    return clone;
  }

  private boolean sourceSupportsIncremental() throws Exception {
    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      if (stream.getStream().getSupportedSyncModes().contains(INCREMENTAL)) {
        return true;
      }
    }
    return false;
  }

  private void assertSameRecords(final List<AirbyteRecordMessage> expected, final List<AirbyteRecordMessage> actual, final String message) {
    final List<AirbyteRecordMessage> prunedExpected = expected.stream().map(this::pruneEmittedAt).collect(Collectors.toList());
    final List<AirbyteRecordMessage> prunedActual = actual
        .stream()
        .map(this::pruneEmittedAt)
        .map(this::pruneCdcMetadata)
        .collect(Collectors.toList());
    assertEquals(prunedExpected.size(), prunedActual.size(), message);
    assertTrue(prunedExpected.containsAll(prunedActual), message);
    assertTrue(prunedActual.containsAll(prunedExpected), message);
  }

  private AirbyteRecordMessage pruneEmittedAt(final AirbyteRecordMessage m) {
    return Jsons.clone(m).withEmittedAt(null);
  }

  private AirbyteRecordMessage pruneCdcMetadata(final AirbyteRecordMessage m) {
    final AirbyteRecordMessage clone = Jsons.clone(m);
    ((ObjectNode) clone.getData()).remove(CDC_LSN);
    ((ObjectNode) clone.getData()).remove(CDC_LOG_FILE);
    ((ObjectNode) clone.getData()).remove(CDC_LOG_POS);
    ((ObjectNode) clone.getData()).remove(CDC_UPDATED_AT);
    ((ObjectNode) clone.getData()).remove(CDC_DELETED_AT);
    return clone;
  }

}
