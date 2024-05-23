/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.source

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.Iterables
import com.google.common.collect.Sets
import io.airbyte.commons.json.Jsons
import io.airbyte.configoss.StandardCheckConnectionOutput
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

private val LOGGER = KotlinLogging.logger {}

abstract class SourceAcceptanceTest : AbstractSourceConnectorTest() {
    /**
     * TODO hack: Various Singer integrations use cursor fields inclusively i.e: they output records
     * whose cursor field >= the provided cursor value. This leads to the last record in a sync to
     * always be the first record in the next sync. This is a fine assumption from a product POV
     * since we offer at-least-once delivery. But for simplicity, the incremental test suite
     * currently assumes that the second incremental read should output no records when provided the
     * state from the first sync. This works for many integrations but not some Singer ones, so we
     * hardcode the list of integrations to skip over when performing those tests.
     */
    private val IMAGES_TO_SKIP_SECOND_INCREMENTAL_READ: Set<String> =
        Sets.newHashSet(
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
            "airbyte/source-jira"
        )

    /**
     * FIXME: Some sources can't guarantee that there will be no events between two sequential sync
     */
    private val IMAGES_TO_SKIP_IDENTICAL_FULL_REFRESHES: Set<String> =
        Sets.newHashSet("airbyte/source-google-workspace-admin-reports", "airbyte/source-kafka")

    /**
     * Specification for integration. Will be passed to integration where appropriate in each test.
     * Should be valid.
     */
    @get:Throws(Exception::class) protected abstract val spec: ConnectorSpecification

    /**
     * The catalog to use to validate the output of read operations. This will be used as follows:
     *
     * Full Refresh syncs will be tested on all the input streams which support it Incremental
     * syncs: - if the stream declares a source-defined cursor, it will be tested with an
     * incremental sync using the default cursor. - if the stream requires a user-defined cursor, it
     * will be tested with the input cursor in both cases, the input [.getState] will be used as the
     * input state.
     */
    @get:Throws(Exception::class) protected abstract val configuredCatalog: ConfiguredAirbyteCatalog

    /** a JSON file representing the state file to use when testing incremental syncs */
    @get:Throws(Exception::class) protected abstract val state: JsonNode?

    /** Verify that a spec operation issued to the connector returns a valid spec. */
    @Test
    @Throws(Exception::class)
    fun testGetSpec() {
        Assertions.assertEquals(
            spec,
            runSpec(),
            "Expected spec output by integration to be equal to spec provided by test runner"
        )
    }

    /**
     * Verify that a check operation issued to the connector with the input config file returns a
     * success response.
     */
    @Test
    @Throws(Exception::class)
    fun testCheckConnection() {
        Assertions.assertEquals(
            StandardCheckConnectionOutput.Status.SUCCEEDED,
            runCheck().status,
            "Expected check connection operation to succeed"
        )
    }

    // /**
    // * Verify that when given invalid credentials, that check connection returns a failed
    // response.
    // * Assume that the {@link TestSource#getFailCheckConfig()} is invalid.
    // */
    // @Test
    // public void testCheckConnectionInvalidCredentials() throws Exception {
    // final OutputAndStatus<StandardCheckConnectionOutput> output = runCheck();
    // assertTrue(output.getOutput().isPresent());
    // assertEquals(Status.FAILED, output.getOutput().get().getStatus());
    // }
    /**
     * Verifies when a discover operation is run on the connector using the given config file, a
     * valid catalog is output by the connector.
     */
    @Test
    @Throws(Exception::class)
    fun testDiscover() {
        runDiscover()
        val discoveredCatalog = lastPersistedCatalog
        Assertions.assertNotNull(discoveredCatalog, "Expected discover to produce a catalog")
        verifyCatalog(discoveredCatalog)
    }

    /** Override this method to check the actual catalog. */
    @Throws(Exception::class)
    protected open fun verifyCatalog(catalog: AirbyteCatalog?) {
        // do nothing by default
    }

    /**
     * Configuring all streams in the input catalog to full refresh mode, verifies that a read
     * operation produces some RECORD messages.
     */
    @Test
    @Throws(Exception::class)
    fun testFullRefreshRead() {
        if (!sourceSupportsFullRefresh()) {
            LOGGER.info("Test skipped. Source does not support full refresh.")
            return
        }

        val catalog = withFullRefreshSyncModes(configuredCatalog)
        val allMessages = runRead(catalog)

        Assertions.assertFalse(
            filterRecords(allMessages).isEmpty(),
            "Expected a full refresh sync to produce records"
        )
        assertFullRefreshMessages(allMessages)
    }

    /** Override this method to perform more specific assertion on the messages. */
    @Throws(Exception::class)
    protected open fun assertFullRefreshMessages(allMessages: List<AirbyteMessage>) {
        // do nothing by default
    }

    /**
     * Configuring all streams in the input catalog to full refresh mode, performs two read
     * operations on all streams which support full refresh syncs. It then verifies that the RECORD
     * messages output from both were identical.
     */
    @Test
    @Throws(Exception::class)
    fun testIdenticalFullRefreshes() {
        if (!sourceSupportsFullRefresh()) {
            LOGGER.info("Test skipped. Source does not support full refresh.")
            return
        }

        if (
            IMAGES_TO_SKIP_IDENTICAL_FULL_REFRESHES.contains(
                imageName.split(":".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()[0]
            )
        ) {
            return
        }

        val configuredCatalog = withFullRefreshSyncModes(configuredCatalog)
        val recordMessagesFirstRun = filterRecords(runRead(configuredCatalog))
        val recordMessagesSecondRun = filterRecords(runRead(configuredCatalog))
        // the worker validates the messages, so we just validate the message, so we do not need to
        // validate
        // again (as long as we use the worker, which we will not want to do long term).
        Assertions.assertFalse(
            recordMessagesFirstRun.isEmpty(),
            "Expected first full refresh to produce records"
        )
        Assertions.assertFalse(
            recordMessagesSecondRun.isEmpty(),
            "Expected second full refresh to produce records"
        )

        assertSameRecords(
            recordMessagesFirstRun,
            recordMessagesSecondRun,
            "Expected two full refresh syncs to produce the same records."
        )
    }

    /**
     * This test verifies that all streams in the input catalog which support incremental sync can
     * do so correctly. It does this by running two read operations on the connector's Docker image:
     * the first takes the configured catalog and config provided to this test as input. It then
     * verifies that the sync produced a non-zero number of RECORD and STATE messages.
     *
     * The second read takes the same catalog and config used in the first test, plus the last STATE
     * message output by the first read operation as the input state file. It verifies that no
     * records are produced (since we read all records in the first sync).
     *
     * This test is performed only for streams which support incremental. Streams which do not
     * support incremental sync are ignored. If no streams in the input catalog support incremental
     * sync, this test is skipped.
     */
    @Test
    @Throws(Exception::class)
    fun testIncrementalSyncWithState() {
        if (!sourceSupportsIncremental()) {
            return
        }

        val configuredCatalog = withSourceDefinedCursors(configuredCatalog)
        // only sync incremental streams
        configuredCatalog.streams =
            configuredCatalog.streams.filter { s: ConfiguredAirbyteStream ->
                s.syncMode == SyncMode.INCREMENTAL
            }

        val airbyteMessages = runRead(configuredCatalog, state)
        val recordMessages = filterRecords(airbyteMessages)
        val stateMessages =
            airbyteMessages
                .filter { m: AirbyteMessage -> m.type == AirbyteMessage.Type.STATE }
                .map { obj: AirbyteMessage -> obj.state }

        Assertions.assertFalse(
            recordMessages.isEmpty(),
            "Expected the first incremental sync to produce records"
        )
        Assertions.assertFalse(
            stateMessages.isEmpty(),
            "Expected incremental sync to produce STATE messages"
        )

        // TODO validate exact records
        if (
            IMAGES_TO_SKIP_SECOND_INCREMENTAL_READ.contains(
                imageName.split(":".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()[0]
            )
        ) {
            return
        }

        // when we run incremental sync again there should be no new records. Run a sync with the
        // latest
        // state message and assert no records were emitted.
        var latestState: JsonNode? = null
        for (stateMessage in stateMessages) {
            if (stateMessage.type == AirbyteStateMessage.AirbyteStateType.STREAM) {
                latestState = Jsons.jsonNode(stateMessages)
                break
            } else if (stateMessage.type == AirbyteStateMessage.AirbyteStateType.GLOBAL) {
                latestState = Jsons.jsonNode(java.util.List.of(Iterables.getLast(stateMessages)))
                break
            } else {
                throw RuntimeException("Unknown state type " + stateMessage.type)
            }
        }

        assert(Objects.nonNull(latestState))
        val secondSyncRecords = filterRecords(runRead(configuredCatalog, latestState))
        Assertions.assertTrue(
            secondSyncRecords.isEmpty(),
            "Expected the second incremental sync to produce no records when given the first sync's output state."
        )
    }

    /**
     * If the source does not support incremental sync, this test is skipped.
     *
     * Otherwise, this test runs two syncs: one where all streams provided in the input catalog sync
     * in full refresh mode, and another where all the streams which in the input catalog which
     * support incremental, sync in incremental mode (streams which don't support incremental sync
     * in full refresh mode). Then, the test asserts that the two syncs produced the same RECORD
     * messages. Any other type of message is disregarded.
     */
    @Test
    @Throws(Exception::class)
    fun testEmptyStateIncrementalIdenticalToFullRefresh() {
        if (!sourceSupportsIncremental()) {
            return
        }

        if (!sourceSupportsFullRefresh()) {
            LOGGER.info("Test skipped. Source does not support full refresh.")
            return
        }

        val configuredCatalog = configuredCatalog
        val fullRefreshCatalog = withFullRefreshSyncModes(configuredCatalog)

        val fullRefreshRecords = filterRecords(runRead(fullRefreshCatalog))
        val emptyStateRecords =
            filterRecords(runRead(configuredCatalog, Jsons.jsonNode(HashMap<Any, Any>())))
        Assertions.assertFalse(
            fullRefreshRecords.isEmpty(),
            "Expected a full refresh sync to produce records"
        )
        Assertions.assertFalse(
            emptyStateRecords.isEmpty(),
            "Expected state records to not be empty"
        )
        assertSameRecords(
            fullRefreshRecords,
            emptyStateRecords,
            "Expected a full refresh sync and incremental sync with no input state to produce identical records"
        )
    }

    /**
     * In order to launch a source on Kubernetes in a pod, we need to be able to wrap the
     * entrypoint. The source connector must specify its entrypoint in the AIRBYTE_ENTRYPOINT
     * variable. This test ensures that the entrypoint environment variable is set.
     */
    @Test
    @Throws(Exception::class)
    fun testEntrypointEnvVar() {
        checkEntrypointEnvVariable()
    }

    protected fun withSourceDefinedCursors(
        catalog: ConfiguredAirbyteCatalog
    ): ConfiguredAirbyteCatalog {
        val clone = Jsons.clone(catalog)
        for (configuredStream in clone.streams) {
            if (
                configuredStream.syncMode == SyncMode.INCREMENTAL &&
                    configuredStream.stream.sourceDefinedCursor != null &&
                    configuredStream.stream.sourceDefinedCursor
            ) {
                configuredStream.cursorField = configuredStream.stream.defaultCursorField
            }
        }
        return clone
    }

    protected fun withFullRefreshSyncModes(
        catalog: ConfiguredAirbyteCatalog
    ): ConfiguredAirbyteCatalog {
        val clone = Jsons.clone(catalog)
        for (configuredStream in clone.streams) {
            if (configuredStream.stream.supportedSyncModes.contains(SyncMode.FULL_REFRESH)) {
                configuredStream.syncMode = SyncMode.FULL_REFRESH
                configuredStream.destinationSyncMode = DestinationSyncMode.OVERWRITE
            }
        }
        return clone
    }

    @Throws(Exception::class)
    private fun sourceSupportsIncremental(): Boolean {
        return sourceSupports(SyncMode.INCREMENTAL)
    }

    @Throws(Exception::class)
    private fun sourceSupportsFullRefresh(): Boolean {
        return sourceSupports(SyncMode.FULL_REFRESH)
    }

    @Throws(Exception::class)
    private fun sourceSupports(syncMode: SyncMode): Boolean {
        val catalog = configuredCatalog
        for (stream in catalog.streams) {
            if (stream.stream.supportedSyncModes.contains(syncMode)) {
                return true
            }
        }
        return false
    }

    private fun assertSameRecords(
        expected: List<AirbyteRecordMessage>,
        actual: List<AirbyteRecordMessage>,
        message: String
    ) {
        val prunedExpected =
            expected
                .stream()
                .map { m: AirbyteRecordMessage -> this.pruneEmittedAt(m) }
                .map { m: AirbyteRecordMessage -> this.pruneCdcMetadata(m) }
                .toList()
        val prunedActual =
            actual
                .map { m: AirbyteRecordMessage -> this.pruneEmittedAt(m) }
                .map { m: AirbyteRecordMessage -> this.pruneCdcMetadata(m) }

        Assertions.assertEquals(prunedExpected.size, prunedActual.size, message)
        Assertions.assertTrue(prunedExpected.containsAll(prunedActual), message)
        Assertions.assertTrue(prunedActual.containsAll(prunedExpected), message)
    }

    private fun pruneEmittedAt(m: AirbyteRecordMessage): AirbyteRecordMessage {
        return Jsons.clone(m).withEmittedAt(null)
    }

    private fun pruneCdcMetadata(m: AirbyteRecordMessage): AirbyteRecordMessage {
        val clone = Jsons.clone(m)
        (clone.data as ObjectNode).remove(CDC_LSN)
        (clone.data as ObjectNode).remove(CDC_LOG_FILE)
        (clone.data as ObjectNode).remove(CDC_LOG_POS)
        (clone.data as ObjectNode).remove(CDC_UPDATED_AT)
        (clone.data as ObjectNode).remove(CDC_DELETED_AT)
        (clone.data as ObjectNode).remove(CDC_EVENT_SERIAL_NO)
        (clone.data as ObjectNode).remove(CDC_DEFAULT_CURSOR)
        return clone
    }

    companion object {
        const val CDC_LSN: String = "_ab_cdc_lsn"
        const val CDC_UPDATED_AT: String = "_ab_cdc_updated_at"
        const val CDC_DELETED_AT: String = "_ab_cdc_deleted_at"
        const val CDC_LOG_FILE: String = "_ab_cdc_log_file"
        const val CDC_LOG_POS: String = "_ab_cdc_log_pos"
        const val CDC_DEFAULT_CURSOR: String = "_ab_cdc_cursor"
        const val CDC_EVENT_SERIAL_NO: String = "_ab_cdc_event_serial_no"

        @JvmStatic
        protected fun filterRecords(
            messages: Collection<AirbyteMessage>
        ): List<AirbyteRecordMessage> {
            return messages
                .filter { m: AirbyteMessage -> m.type == AirbyteMessage.Type.RECORD }
                .map { obj: AirbyteMessage -> obj.record }
        }

        @JvmStatic
        fun extractLatestState(stateMessages: List<AirbyteStateMessage>): JsonNode? {
            var latestState: JsonNode? = null
            for (stateMessage in stateMessages) {
                if (stateMessage.type == AirbyteStateMessage.AirbyteStateType.STREAM) {
                    latestState = Jsons.jsonNode(stateMessages)
                    break
                } else if (stateMessage.type == AirbyteStateMessage.AirbyteStateType.GLOBAL) {
                    latestState =
                        Jsons.jsonNode(java.util.List.of(Iterables.getLast(stateMessages)))
                    break
                } else {
                    throw RuntimeException("Unknown state type " + stateMessage.type)
                }
            }
            return latestState
        }
    }
}
