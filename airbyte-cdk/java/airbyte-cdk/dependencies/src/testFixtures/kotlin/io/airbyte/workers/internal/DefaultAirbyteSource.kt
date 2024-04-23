/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.internal

import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Preconditions
import io.airbyte.commons.features.FeatureFlags
import io.airbyte.commons.io.IOs
import io.airbyte.commons.io.LineGobbler
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.logging.LoggingHelper
import io.airbyte.commons.logging.MdcScope
import io.airbyte.commons.protocol.DefaultProtocolSerializer
import io.airbyte.commons.protocol.ProtocolSerializer
import io.airbyte.configoss.WorkerSourceConfig
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.workers.TestHarnessUtils
import io.airbyte.workers.WorkerConstants
import io.airbyte.workers.process.IntegrationLauncher
import java.nio.file.Path
import java.time.Duration
import java.time.temporal.ChronoUnit
import java.util.*
import java.util.List
import java.util.concurrent.TimeUnit
import kotlin.collections.Iterator
import kotlin.collections.Set
import kotlin.collections.contains
import kotlin.collections.setOf
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class DefaultAirbyteSource
@VisibleForTesting
internal constructor(
    private val integrationLauncher: IntegrationLauncher,
    private val streamFactory: AirbyteStreamFactory,
    private val heartbeatMonitor: HeartbeatMonitor,
    private val protocolSerializer: ProtocolSerializer,
    featureFlags: FeatureFlags
) : AirbyteSource {
    private var sourceProcess: Process? = null
    private var messageIterator: Iterator<AirbyteMessage?>? = null

    private var exitValueIsSet = false
    @get:Throws(IllegalStateException::class)
    override var exitValue: Int = 0
        get() {
            Preconditions.checkState(
                sourceProcess != null,
                "Source process is null, cannot retrieve exit value."
            )
            Preconditions.checkState(
                !sourceProcess!!.isAlive,
                "Source process is still alive, cannot retrieve exit value."
            )

            if (!exitValueIsSet) {
                exitValueIsSet = true
                field = sourceProcess!!.exitValue()
            }

            return field
        }
        private set
    private val featureFlagLogConnectorMsgs = featureFlags.logConnectorMessages()

    constructor(
        integrationLauncher: IntegrationLauncher,
        featureFlags: FeatureFlags
    ) : this(
        integrationLauncher,
        DefaultAirbyteStreamFactory(CONTAINER_LOG_MDC_BUILDER),
        DefaultProtocolSerializer(),
        featureFlags
    )

    constructor(
        integrationLauncher: IntegrationLauncher,
        streamFactory: AirbyteStreamFactory,
        protocolSerializer: ProtocolSerializer,
        featureFlags: FeatureFlags
    ) : this(
        integrationLauncher,
        streamFactory,
        HeartbeatMonitor(HEARTBEAT_FRESH_DURATION),
        protocolSerializer,
        featureFlags
    )

    @Throws(Exception::class)
    override fun start(sourceConfig: WorkerSourceConfig, jobRoot: Path) {
        Preconditions.checkState(sourceProcess == null)

        sourceProcess =
            integrationLauncher.read(
                jobRoot,
                WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
                Jsons.serialize(sourceConfig.sourceConnectionConfiguration),
                WorkerConstants.SOURCE_CATALOG_JSON_FILENAME,
                protocolSerializer.serialize(sourceConfig.catalog),
                if (sourceConfig.state == null) null
                else
                    WorkerConstants
                        .INPUT_STATE_JSON_FILENAME, // TODO We should be passing a typed state here
                // and use the protocolSerializer
                if (sourceConfig.state == null) null else Jsons.serialize(sourceConfig.state.state)
            )
        // stdout logs are logged elsewhere since stdout also contains data
        LineGobbler.gobble(
            sourceProcess!!.errorStream,
            { msg: String -> LOGGER.error(msg) },
            "airbyte-source",
            CONTAINER_LOG_MDC_BUILDER
        )

        logInitialStateAsJSON(sourceConfig)

        val acceptedMessageTypes =
            List.of(
                AirbyteMessage.Type.RECORD,
                AirbyteMessage.Type.STATE,
                AirbyteMessage.Type.TRACE,
                AirbyteMessage.Type.CONTROL
            )
        messageIterator =
            streamFactory
                .create(IOs.newBufferedReader(sourceProcess!!.inputStream))
                .peek { message: AirbyteMessage -> heartbeatMonitor.beat() }
                .filter { message: AirbyteMessage -> acceptedMessageTypes.contains(message.type) }
                .iterator()
    }

    override val isFinished: Boolean
        get() {
            Preconditions.checkState(sourceProcess != null)

            /*
             * As this check is done on every message read, it is important for this operation to be efficient.
             * Short circuit early to avoid checking the underlying process. note: hasNext is blocking.
             */
            return !messageIterator!!.hasNext() && !sourceProcess!!.isAlive
        }

    override fun attemptRead(): Optional<AirbyteMessage> {
        Preconditions.checkState(sourceProcess != null)

        return Optional.ofNullable(
            if (messageIterator!!.hasNext()) messageIterator!!.next() else null
        )
    }

    @Throws(Exception::class)
    override fun close() {
        if (sourceProcess == null) {
            LOGGER.debug("Source process already exited")
            return
        }

        LOGGER.debug("Closing source process")
        TestHarnessUtils.gentleClose(
            sourceProcess,
            GRACEFUL_SHUTDOWN_DURATION.toMillis(),
            TimeUnit.MILLISECONDS
        )

        if (sourceProcess!!.isAlive || !IGNORED_EXIT_CODES.contains(exitValue)) {
            val message =
                if (sourceProcess!!.isAlive) "Source has not terminated "
                else "Source process exit with code " + exitValue
            LOGGER.warn("$message. This warning is normal if the job was cancelled.")
        }
    }

    @Throws(Exception::class)
    override fun cancel() {
        LOGGER.info("Attempting to cancel source process...")

        if (sourceProcess == null) {
            LOGGER.info("Source process no longer exists, cancellation is a no-op.")
        } else {
            LOGGER.info("Source process exists, cancelling...")
            TestHarnessUtils.cancelProcess(sourceProcess)
            LOGGER.info("Cancelled source process!")
        }
    }

    private fun logInitialStateAsJSON(sourceConfig: WorkerSourceConfig) {
        if (!featureFlagLogConnectorMsgs) {
            return
        }

        if (sourceConfig.state == null) {
            LOGGER.info("source starting state | empty")
            return
        }

        LOGGER.info("source starting state | " + Jsons.serialize(sourceConfig.state.state))
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(DefaultAirbyteSource::class.java)

        private val HEARTBEAT_FRESH_DURATION: Duration = Duration.of(5, ChronoUnit.MINUTES)
        private val GRACEFUL_SHUTDOWN_DURATION: Duration = Duration.of(1, ChronoUnit.MINUTES)
        val IGNORED_EXIT_CODES: Set<Int> =
            setOf(
                0, // Normal exit
                143 // SIGTERM
            )

        val CONTAINER_LOG_MDC_BUILDER: MdcScope.Builder =
            MdcScope.Builder()
                .setLogPrefix("source")
                .setPrefixColor(LoggingHelper.Color.BLUE_BACKGROUND)
    }
}
