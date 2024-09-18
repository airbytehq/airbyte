/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Preconditions
import com.google.common.collect.Lists
import datadog.trace.api.Trace
import io.airbyte.cdk.integrations.util.ConnectorExceptionHandler
import io.airbyte.cdk.integrations.util.concurrent.ConcurrentStreamConsumer
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.features.FeatureFlags
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.stream.AirbyteStreamStatusHolder
import io.airbyte.commons.stream.StreamStatusUtils
import io.airbyte.commons.string.Strings
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.validation.json.JsonSchemaValidator
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.*
import java.lang.reflect.Method
import java.nio.charset.StandardCharsets
import java.nio.file.Path
import java.time.Instant
import java.util.*
import java.util.concurrent.*
import java.util.function.Consumer
import org.apache.commons.lang3.ThreadUtils
import org.apache.commons.lang3.concurrent.BasicThreadFactory

private val LOGGER = KotlinLogging.logger {}
/**
 * Accepts EITHER a destination or a source. Routes commands from the commandline to the appropriate
 * methods on the integration. Keeps itself DRY for methods that are common between source and
 * destination.
 */
class IntegrationRunner
@VisibleForTesting
internal constructor(
    cliParser: IntegrationCliParser,
    outputRecordCollector: Consumer<AirbyteMessage>,
    destination: Destination?,
    source: Source?
) {
    private val cliParser: IntegrationCliParser
    private val outputRecordCollector: Consumer<AirbyteMessage>
    private val integration: Integration
    private val destination: Destination?
    private val source: Source?
    private val featureFlags: FeatureFlags

    constructor(
        destination: Destination?
    ) : this(
        IntegrationCliParser(),
        Consumer<AirbyteMessage> { message: AirbyteMessage ->
            Destination.Companion.defaultOutputRecordCollector(message)
        },
        destination,
        null
    )

    constructor(
        source: Source?
    ) : this(
        IntegrationCliParser(),
        Consumer<AirbyteMessage> { message: AirbyteMessage ->
            Destination.Companion.defaultOutputRecordCollector(message)
        },
        null,
        source
    )

    init {
        Preconditions.checkState(
            (destination != null) xor (source != null),
            "can only pass in a destination or a source"
        )
        threadCreationInfo.set(ThreadCreationInfo())
        this.cliParser = cliParser
        this.outputRecordCollector = outputRecordCollector
        // integration iface covers the commands that are the same for both source and destination.
        integration = source ?: destination!!
        this.source = source
        this.destination = destination
        this.featureFlags = EnvVariableFeatureFlags()
        validator = JsonSchemaValidator()

        Thread.setDefaultUncaughtExceptionHandler(AirbyteExceptionHandler())
    }

    @VisibleForTesting
    internal constructor(
        cliParser: IntegrationCliParser,
        outputRecordCollector: Consumer<AirbyteMessage>,
        destination: Destination?,
        source: Source?,
        jsonSchemaValidator: JsonSchemaValidator
    ) : this(cliParser, outputRecordCollector, destination, source) {
        validator = jsonSchemaValidator
    }

    @Trace(operationName = "RUN_OPERATION")
    @Throws(Exception::class)
    @JvmOverloads
    fun run(
        args: Array<String>,
        exceptionHandler: ConnectorExceptionHandler = ConnectorExceptionHandler()
    ) {
        val parsed = cliParser.parse(args)
        try {
            runInternal(parsed, exceptionHandler)
        } catch (e: Exception) {
            throw e
        }
    }

    @Throws(Exception::class)
    private fun runInternal(
        parsed: IntegrationConfig,
        exceptionHandler: ConnectorExceptionHandler
    ) {
        LOGGER.info { "Running integration: ${integration.javaClass.name}" }
        LOGGER.info { "Command: ${parsed.command}" }
        LOGGER.info { "Integration config: $parsed" }

        try {
            when (parsed.command) {
                Command.SPEC ->
                    outputRecordCollector.accept(
                        AirbyteMessage()
                            .withType(AirbyteMessage.Type.SPEC)
                            .withSpec(integration.spec())
                    )
                Command.CHECK -> {
                    val config = parseConfig(parsed.getConfigPath())
                    if (integration is Destination) {
                        DestinationConfig.Companion.initialize(config, integration.isV2Destination)
                    }
                    try {
                        validateConfig(integration.spec().connectionSpecification, config, "CHECK")
                    } catch (e: Exception) {
                        // if validation fails don't throw an exception, return a failed connection
                        // check message
                        outputRecordCollector.accept(
                            AirbyteMessage()
                                .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                                .withConnectionStatus(
                                    AirbyteConnectionStatus()
                                        .withStatus(AirbyteConnectionStatus.Status.FAILED)
                                        .withMessage(e.message)
                                )
                        )
                    }

                    outputRecordCollector.accept(
                        AirbyteMessage()
                            .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                            .withConnectionStatus(integration.check(config))
                    )
                }
                Command.DISCOVER -> {
                    val config = parseConfig(parsed.getConfigPath())
                    validateConfig(integration.spec().connectionSpecification, config, "DISCOVER")
                    outputRecordCollector.accept(
                        AirbyteMessage()
                            .withType(AirbyteMessage.Type.CATALOG)
                            .withCatalog(source!!.discover(config))
                    )
                }
                Command.READ -> {
                    val config = parseConfig(parsed.getConfigPath())
                    validateConfig(integration.spec().connectionSpecification, config, "READ")
                    val catalog =
                        parseConfig(parsed.getCatalogPath(), ConfiguredAirbyteCatalog::class.java)!!
                    val stateOptional =
                        parsed.getStatePath().map { path: Path -> parseConfig(path) }
                    try {
                        if (featureFlags.concurrentSourceStreamRead()) {
                            LOGGER.info { "Concurrent source stream read enabled." }
                            readConcurrent(config, catalog, stateOptional)
                        } else {
                            readSerial(config, catalog, stateOptional)
                        }
                    } finally {
                        if (source is AutoCloseable) {
                            (source as AutoCloseable).close()
                        }
                    }
                }
                Command.WRITE -> {
                    try {
                        val config = parseConfig(parsed.getConfigPath())
                        validateConfig(integration.spec().connectionSpecification, config, "WRITE")
                        // save config to singleton
                        DestinationConfig.Companion.initialize(
                            config,
                            (integration as Destination).isV2Destination
                        )
                        val catalog =
                            parseConfig(
                                parsed.getCatalogPath(),
                                ConfiguredAirbyteCatalog::class.java
                            )!!

                        destination!!
                            .getSerializedMessageConsumer(config, catalog, outputRecordCollector)
                            .use { consumer -> consumeWriteStream(consumer!!) }
                    } finally {
                        stopOrphanedThreads()
                    }
                }
            }
        } catch (e: Exception) {
            exceptionHandler.handleException(e, parsed.command, outputRecordCollector)
        }
        LOGGER.info { "Completed integration: ${integration.javaClass.name}" }
    }

    private fun produceMessages(
        messageIterator: AutoCloseableIterator<AirbyteMessage>,
        recordCollector: Consumer<AirbyteMessage>
    ) {
        messageIterator.airbyteStream.ifPresent { s: AirbyteStreamNameNamespacePair ->
            LOGGER.debug { "Producing messages for stream $s..." }
        }
        messageIterator.forEachRemaining(recordCollector)
        messageIterator.airbyteStream.ifPresent { s: AirbyteStreamNameNamespacePair ->
            LOGGER.debug { "Finished producing messages for stream $s..." }
        }
    }

    @Throws(Exception::class)
    private fun readConcurrent(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        stateOptional: Optional<JsonNode>
    ) {
        val streams = source!!.readStreams(config, catalog, stateOptional.orElse(null))

        try {
            ConcurrentStreamConsumer(
                    { stream: AutoCloseableIterator<AirbyteMessage> ->
                        this.consumeFromStream(stream)
                    },
                    streams!!.size
                )
                .use { streamConsumer ->
                    /*
                     * Break the streams into partitions equal to the number of concurrent streams supported by the
                     * stream consumer.
                     */
                    val partitionSize = streamConsumer.parallelism
                    val partitions = Lists.partition(streams.toList(), partitionSize)

                    // Submit each stream partition for concurrent execution
                    partitions.forEach(
                        Consumer { partition: List<AutoCloseableIterator<AirbyteMessage>> ->
                            streamConsumer.accept(partition)
                        }
                    )

                    // Check for any exceptions that were raised during the concurrent execution
                    if (streamConsumer.exception.isPresent) {
                        throw streamConsumer.exception.get()
                    }
                }
        } catch (e: Exception) {
            LOGGER.error(e) { "Unable to perform concurrent read." }
            throw e
        } finally {
            stopOrphanedThreads()
        }
    }

    @Throws(Exception::class)
    private fun readSerial(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        stateOptional: Optional<JsonNode>
    ) {
        try {
            source!!.read(config, catalog, stateOptional.orElse(null)).use { messageIterator ->
                produceMessages(messageIterator, outputRecordCollector)
            }
        } finally {
            stopOrphanedThreads()
        }
    }

    private fun consumeFromStream(stream: AutoCloseableIterator<AirbyteMessage>) {
        try {
            val streamStatusTrackingRecordConsumer =
                StreamStatusUtils.statusTrackingRecordCollector(
                    stream,
                    outputRecordCollector,
                    Optional.of(
                        Consumer { obj: AirbyteStreamStatusHolder ->
                            AirbyteTraceMessageUtility.emitStreamStatusTrace(obj)
                        }
                    )
                )
            produceMessages(stream, streamStatusTrackingRecordConsumer)
        } catch (e: Exception) {
            stream.airbyteStream.ifPresent { s: AirbyteStreamNameNamespacePair ->
                LOGGER.error(e) { "Failed to consume from stream $s." }
            }
            throw RuntimeException(e)
        }
    }

    data class OrphanedThreadInfo
    private constructor(
        val thread: Thread,
        val threadCreationInfo: ThreadCreationInfo,
        val lastStackTrace: List<StackTraceElement>
    ) {
        fun getLogString(): String {
            return String.format(
                "%s (%s)\n Thread stacktrace: %s",
                thread.name,
                thread.state,
                lastStackTrace.joinToString("\n        at ")
            )
        }

        companion object {
            fun getAll(): List<OrphanedThreadInfo> {
                return ThreadUtils.getAllThreads().mapNotNull { getForThread(it) }
            }

            fun getForThread(thread: Thread): OrphanedThreadInfo? {
                val threadCreationInfo =
                    getMethod.invoke(threadCreationInfo, thread) as ThreadCreationInfo?
                val stack = thread.stackTrace.asList()
                if (threadCreationInfo == null) {
                    return null
                }
                return OrphanedThreadInfo(thread, threadCreationInfo, stack)
            }

            // ThreadLocal.get(Thread) is private. So we open it and keep a reference to the
            // opened method
            private val getMethod: Method =
                ThreadLocal::class.java.getDeclaredMethod("get", Thread::class.java).also {
                    it.isAccessible = true
                }
        }
    }

    class ThreadCreationInfo {
        val stack: List<StackTraceElement> = Thread.currentThread().stackTrace.asList()
        val time: Instant = Instant.now()
        override fun toString(): String {
            return "creationStack=${stack.joinToString("\n  ")}\ncreationTime=$time"
        }
    }

    companion object {
        private val threadCreationInfo: InheritableThreadLocal<ThreadCreationInfo> =
            object : InheritableThreadLocal<ThreadCreationInfo>() {
                override fun childValue(parentValue: ThreadCreationInfo?): ThreadCreationInfo {
                    return ThreadCreationInfo()
                }
            }

        const val TYPE_AND_DEDUPE_THREAD_NAME: String = "type-and-dedupe"

        /**
         * Filters threads that should not be considered when looking for orphaned threads at
         * shutdown of the integration runner.
         *
         * **N.B.** Daemon threads don't block the JVM if the main `currentThread` exits, so they
         * are not problematic. Additionally, ignore database connection pool threads, which stay
         * active so long as the database connection pool is open.
         */
        @VisibleForTesting
        private val orphanedThreadPredicates: MutableList<(OrphanedThreadInfo) -> Boolean> =
            mutableListOf({ runningThreadInfo: OrphanedThreadInfo ->
                (runningThreadInfo.thread.name != Thread.currentThread().name &&
                    !runningThreadInfo.thread.isDaemon &&
                    TYPE_AND_DEDUPE_THREAD_NAME != runningThreadInfo.thread.name)
            })

        const val INTERRUPT_THREAD_DELAY_MINUTES: Int = 1
        const val EXIT_THREAD_DELAY_MINUTES: Int = 2

        const val FORCED_EXIT_CODE: Int = 2

        private val EXIT_HOOK = Runnable { System.exit(FORCED_EXIT_CODE) }

        private lateinit var validator: JsonSchemaValidator

        @Throws(Exception::class)
        internal fun consumeWriteStream(
            consumer: SerializedAirbyteMessageConsumer,
            inputStream: InputStream = System.`in`
        ) {
            LOGGER.info { "Starting buffered read of input stream" }
            consumer.start()
            inputStream.bufferedReader(StandardCharsets.UTF_8).use {
                var emptyLines = 0
                it.lines().forEach { line: String ->
                    if (line.isNotEmpty()) {
                        consumer.accept(line, line.toByteArray(StandardCharsets.UTF_8).size)
                    } else {
                        emptyLines++
                        // We've occasionally seen this loop not exit
                        // maybe it's because we keep getting streams of empty lines?
                        // TODO: Monitor the logs for occurrences of this log line and if this isn't
                        // an issue, remove it.
                        if (emptyLines % 1_000 == 0 && emptyLines < 10_000) {
                            LOGGER.warn { "Encountered $emptyLines empty lines during execution" }
                        }
                    }
                }
                if (emptyLines > 0) {
                    LOGGER.warn { "Encountered $emptyLines empty lines in the input stream." }
                }
            }
            LOGGER.info { "Finished buffered read of input stream" }
        }

        @JvmStatic
        fun addOrphanedThreadFilter(predicate: (OrphanedThreadInfo) -> (Boolean)) {
            orphanedThreadPredicates.add(predicate)
        }

        fun filterOrphanedThread(threadInfo: OrphanedThreadInfo): Boolean {
            return orphanedThreadPredicates.all { it(threadInfo) }
        }

        /**
         * Stops any non-daemon threads that could block the JVM from exiting when the main thread
         * is done.
         *
         * If any active non-daemon threads would be left as orphans, this method will schedule some
         * interrupt/exit hooks after giving it some time delay to close up properly. It is
         * generally preferred to have a proper closing sequence from children threads instead of
         * interrupting or force exiting the process, so this mechanism serve as a fallback while
         * surfacing warnings in logs for maintainers to fix the code behavior instead.
         *
         * @param exitHook The [Runnable] exit hook to execute for any orphaned threads.
         * @param interruptTimeDelay The time to delay execution of the orphaned thread interrupt
         * attempt.
         * @param interruptTimeUnit The time unit of the interrupt delay.
         * @param exitTimeDelay The time to delay execution of the orphaned thread exit hook.
         * @param exitTimeUnit The time unit of the exit delay.
         */
        @VisibleForTesting
        fun stopOrphanedThreads(
            exitHook: Runnable = EXIT_HOOK,
            interruptTimeDelay: Int = INTERRUPT_THREAD_DELAY_MINUTES,
            interruptTimeUnit: TimeUnit = TimeUnit.MINUTES,
            exitTimeDelay: Int = EXIT_THREAD_DELAY_MINUTES,
            exitTimeUnit: TimeUnit = TimeUnit.MINUTES
        ) {
            val currentThread = Thread.currentThread()

            val runningThreadInfos = OrphanedThreadInfo.getAll().filter(::filterOrphanedThread)
            if (runningThreadInfos.isNotEmpty()) {
                LOGGER.warn {
                    """
                  The main thread is exiting while children non-daemon threads from a connector are still active.
                  Ideally, this situation should not happen...
                  Please check with maintainers if the connector or library code should safely clean up its threads before quitting instead.
                  The main thread is: ${dumpThread(currentThread)}
                  """.trimIndent()
                }

                val scheduledExecutorService =
                    Executors.newSingleThreadScheduledExecutor(
                        BasicThreadFactory
                            .Builder() // this thread executor will create daemon threads, so it
                            // does not block exiting if all other active
                            // threads are already stopped.
                            .daemon(true)
                            .build()
                    )
                for (runningThreadInfo in runningThreadInfos) {
                    val str = "Active non-daemon thread info: ${runningThreadInfo.getLogString()}"
                    LOGGER.warn { str }
                    // even though the main thread is already shutting down, we still leave some
                    // chances to the children
                    // threads to close properly on their own.
                    // So, we schedule an interrupt hook after a fixed time delay instead...
                    scheduledExecutorService.schedule(
                        { runningThreadInfo.thread.interrupt() },
                        interruptTimeDelay.toLong(),
                        interruptTimeUnit
                    )
                }
                scheduledExecutorService.schedule(
                    {
                        if (
                            ThreadUtils.getAllThreads().any { runningThread: Thread ->
                                !runningThread.isDaemon && runningThread.name != currentThread.name
                            }
                        ) {
                            LOGGER.error {
                                "Failed to interrupt children non-daemon threads, forcefully exiting NOW...\n"
                            }
                            exitHook.run()
                        }
                    },
                    exitTimeDelay.toLong(),
                    exitTimeUnit
                )
            }
        }

        private fun dumpThread(thread: Thread): String {
            OrphanedThreadInfo.getForThread(thread)
            return String.format(
                "%s (%s)\n Thread stacktrace: %s",
                thread.name,
                thread.state,
                Strings.join(java.util.List.of(*thread.stackTrace), "\n        at ")
            )
        }

        @Throws(Exception::class)
        private fun validateConfig(
            schemaJson: JsonNode,
            objectJson: JsonNode,
            operationType: String
        ) {
            val validationResult = validator.validate(schemaJson, objectJson)
            if (validationResult.isNotEmpty()) {
                throw Exception(
                    String.format(
                        "Verification error(s) occurred for %s. Errors: %s ",
                        operationType,
                        validationResult
                    )
                )
            }
        }

        fun parseConfig(path: Path?): JsonNode {
            return Jsons.deserialize(IOs.readFile(path))
        }

        private fun <T> parseConfig(path: Path?, klass: Class<T>): T? {
            val jsonNode = parseConfig(path)
            return Jsons.`object`(jsonNode, klass)
        }

        /** @param connectorImage Expected format: [organization/]image[:version] */
        @VisibleForTesting
        fun parseConnectorVersion(connectorImage: String?): String {
            if (connectorImage == null || connectorImage == "") {
                return "unknown"
            }

            val tokens =
                connectorImage.split(":".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
            return tokens[tokens.size - 1]
        }
    }
}
