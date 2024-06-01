/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.internal

import com.google.common.base.Charsets
import com.google.common.base.Preconditions
import io.airbyte.commons.io.IOs
import io.airbyte.commons.io.LineGobbler
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.logging.LoggingHelper
import io.airbyte.commons.logging.MdcScope
import io.airbyte.commons.protocol.DefaultProtocolSerializer
import io.airbyte.commons.protocol.ProtocolSerializer
import io.airbyte.configoss.WorkerDestinationConfig
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.workers.TestHarnessUtils
import io.airbyte.workers.WorkerConstants
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.process.IntegrationLauncher
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.BufferedWriter
import java.io.IOException
import java.io.OutputStreamWriter
import java.nio.file.Path
import java.util.*
import java.util.List
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.collections.Iterator
import kotlin.collections.Map
import kotlin.collections.Set
import kotlin.collections.contains
import kotlin.collections.setOf

private val LOGGER = KotlinLogging.logger {}

class DefaultAirbyteDestination
@JvmOverloads
constructor(
    private val integrationLauncher: IntegrationLauncher,
    private val streamFactory: AirbyteStreamFactory =
        DefaultAirbyteStreamFactory(createContainerLogMdcBuilder()),
    private val messageWriterFactory: AirbyteMessageBufferedWriterFactory =
        DefaultAirbyteMessageBufferedWriterFactory(),
    private val protocolSerializer: ProtocolSerializer = DefaultProtocolSerializer()
) : AirbyteDestination {
    private val inputHasEnded = AtomicBoolean(false)

    private var destinationProcess: Process? = null
    private var writer: AirbyteMessageBufferedWriter? = null
    private var messageIterator: Iterator<AirbyteMessage>? = null

    private var exitValueIsSet = false
    override val exitValue: Int
        get() {
            Preconditions.checkState(
                destinationProcess != null,
                "Destination process is null, cannot retrieve exit value."
            )
            Preconditions.checkState(
                !destinationProcess!!.isAlive,
                "Destination process is still alive, cannot retrieve exit value."
            )
            return destinationProcess!!.exitValue()
        }

    @Throws(IOException::class, TestHarnessException::class)
    override fun start(
        destinationConfig: WorkerDestinationConfig,
        jobRoot: Path,
        additionalEnvironmentVariables: Map<String, String>
    ) {
        Preconditions.checkState(destinationProcess == null)

        LOGGER.info("Running destination...")
        destinationProcess =
            integrationLauncher.write(
                jobRoot,
                WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
                Jsons.serialize(destinationConfig.destinationConnectionConfiguration),
                WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME,
                protocolSerializer.serialize(destinationConfig.catalog),
                additionalEnvironmentVariables
            )
        // stdout logs are logged elsewhere since stdout also contains data
        LineGobbler.gobble(
            destinationProcess!!.errorStream,
            { msg: String -> LOGGER.error(msg) },
            "airbyte-destination",
            createContainerLogMdcBuilder()
        )

        writer =
            messageWriterFactory.createWriter(
                BufferedWriter(
                    OutputStreamWriter(destinationProcess!!.outputStream, Charsets.UTF_8)
                )
            )

        val acceptedMessageTypes =
            List.of(
                AirbyteMessage.Type.STATE,
                AirbyteMessage.Type.TRACE,
                AirbyteMessage.Type.CONTROL
            )
        messageIterator =
            streamFactory
                .create(IOs.newBufferedReader(destinationProcess!!.inputStream))
                .filter { message: AirbyteMessage -> acceptedMessageTypes.contains(message.type) }
                .iterator()
    }

    @Throws(IOException::class)
    override fun accept(message: AirbyteMessage) {
        Preconditions.checkState(destinationProcess != null && !inputHasEnded.get())

        writer!!.write(message)
    }

    @Throws(IOException::class)
    override fun notifyEndOfInput() {
        Preconditions.checkState(destinationProcess != null && !inputHasEnded.get())

        writer!!.flush()
        writer!!.close()
        inputHasEnded.set(true)
    }

    @Throws(Exception::class)
    override fun close() {
        if (destinationProcess == null) {
            LOGGER.debug("Destination process already exited")
            return
        }

        if (!inputHasEnded.get()) {
            notifyEndOfInput()
        }

        LOGGER.debug("Closing destination process")
        TestHarnessUtils.gentleClose(destinationProcess, 1, TimeUnit.MINUTES)
        if (destinationProcess!!.isAlive || !IGNORED_EXIT_CODES.contains(exitValue)) {
            val message =
                if (destinationProcess!!.isAlive) "Destination has not terminated "
                else "Destination process exit with code " + exitValue
            throw TestHarnessException("$message. This warning is normal if the job was cancelled.")
        }
    }

    @Throws(Exception::class)
    override fun cancel() {
        LOGGER.info("Attempting to cancel destination process...")

        if (destinationProcess == null) {
            LOGGER.info("Destination process no longer exists, cancellation is a no-op.")
        } else {
            LOGGER.info("Destination process exists, cancelling...")
            TestHarnessUtils.cancelProcess(destinationProcess)
            LOGGER.info("Cancelled destination process!")
        }
    }

    override fun isFinished(): Boolean {
        Preconditions.checkState(destinationProcess != null)
        /*
         * As this check is done on every message read, it is important for this operation to be efficient.
         * Short circuit early to avoid checking the underlying process. Note: hasNext is blocking.
         */
        return !messageIterator!!.hasNext() && !destinationProcess!!.isAlive
    }

    override fun attemptRead(): Optional<AirbyteMessage> {
        Preconditions.checkState(destinationProcess != null)

        return Optional.ofNullable(
            if (messageIterator!!.hasNext()) messageIterator!!.next() else null
        )
    }

    companion object {

        fun createContainerLogMdcBuilder(): MdcScope.Builder =
            MdcScope.Builder()
                .setLogPrefix("destination")
                .setPrefixColor(LoggingHelper.Color.YELLOW_BACKGROUND)
        val IGNORED_EXIT_CODES: Set<Int> =
            setOf(
                0, // Normal exit
                143 // SIGTERM
            )
    }
}
