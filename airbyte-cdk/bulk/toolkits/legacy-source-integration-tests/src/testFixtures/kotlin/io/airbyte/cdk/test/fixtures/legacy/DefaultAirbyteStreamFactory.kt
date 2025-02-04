package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import io.airbyte.protocol.models.AirbyteLogMessage
import io.airbyte.protocol.models.AirbyteMessage
import io.github.oshai.kotlinlogging.KLogger
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.BufferedReader
import java.lang.reflect.InvocationTargetException
import java.nio.charset.StandardCharsets
import java.text.CharacterIterator
import java.text.StringCharacterIterator
import java.time.Instant
import java.util.*
import java.util.stream.Stream

private val LOGGER = KotlinLogging.logger {}
/**
 * Creates a stream from an input stream. The produced stream attempts to parse each line of the
 * InputStream into a AirbyteMessage. If the line cannot be parsed into a AirbyteMessage it is
 * dropped. Each record MUST be new line separated.
 *
 * If a line starts with a AirbyteMessage and then has other characters after it, that
 * AirbyteMessage will still be parsed. If there are multiple AirbyteMessage records on the same
 * line, only the first will be parsed.
 */
class DefaultAirbyteStreamFactory : AirbyteStreamFactory {
    private val MAX_SIZE_RATIO = 0.8

    private val containerLogMdcBuilder: MdcScope.Builder
    private val protocolValidator: AirbyteProtocolPredicate
    protected val logger: KLogger
    private val maxMemory: Long
    private val exceptionClass: Optional<Class<out RuntimeException>>

    @JvmOverloads
    constructor(
        containerLogMdcBuilder: MdcScope.Builder = MdcScope.DEFAULT_BUILDER
    ) : this(
        AirbyteProtocolPredicate(),
        LOGGER,
        containerLogMdcBuilder,
        Optional.empty<Class<out RuntimeException>>()
    )

    /**
     * Create a default airbyte stream, if a `messageSizeExceptionClass` is not empty, the message
     * size will be checked and if it more than the available memory * MAX_SIZE_RATIO the sync will
     * be failed by throwing the exception provided. The exception must have a constructor that
     * accept a string.
     */
    internal constructor(
        protocolPredicate: AirbyteProtocolPredicate,
        logger: KLogger,
        containerLogMdcBuilder: MdcScope.Builder,
        messageSizeExceptionClass: Optional<Class<out RuntimeException>>
    ) {
        protocolValidator = protocolPredicate
        this.logger = logger
        this.containerLogMdcBuilder = containerLogMdcBuilder
        this.exceptionClass = messageSizeExceptionClass
        this.maxMemory = Runtime.getRuntime().maxMemory()
    }

    @VisibleForTesting
    internal constructor(
        protocolPredicate: AirbyteProtocolPredicate,
        logger: KLogger,
        containerLogMdcBuilder: MdcScope.Builder,
        messageSizeExceptionClass: Optional<Class<out RuntimeException>>,
        maxMemory: Long
    ) {
        protocolValidator = protocolPredicate
        this.logger = logger
        this.containerLogMdcBuilder = containerLogMdcBuilder
        this.exceptionClass = messageSizeExceptionClass
        this.maxMemory = maxMemory
    }

    override fun create(bufferedReader: BufferedReader): Stream<AirbyteMessage> {
        return bufferedReader
            .lines()
            .peek { str: String ->
                if (exceptionClass.isPresent) {
                    val messageSize = str.toByteArray(StandardCharsets.UTF_8).size.toLong()
                    if (messageSize > maxMemory * MAX_SIZE_RATIO) {
                        try {
                            val errorMessage =
                                String.format(
                                    "Airbyte has received a message at %s UTC which is larger than %s (size: %s). The sync has been failed to prevent running out of memory.",
                                    Instant.now(),
                                    humanReadableByteCountSI(maxMemory),
                                    humanReadableByteCountSI(messageSize)
                                )
                            throw exceptionClass
                                .get()
                                .getConstructor(String::class.java)
                                .newInstance(errorMessage)!!
                        } catch (e: InstantiationException) {
                            throw RuntimeException(e)
                        } catch (e: IllegalAccessException) {
                            throw RuntimeException(e)
                        } catch (e: InvocationTargetException) {
                            throw RuntimeException(e)
                        } catch (e: NoSuchMethodException) {
                            throw RuntimeException(e)
                        }
                    }
                }
            }
            .flatMap { line: String -> this.parseJson(line) }
            .filter { json: JsonNode -> this.validate(json) }
            .flatMap { json: JsonNode -> this.toAirbyteMessage(json) }
            .filter { message: AirbyteMessage -> this.filterLog(message) }
    }

    protected fun parseJson(line: String?): Stream<JsonNode> {
        val jsonLine = Jsons.tryDeserializeWithoutWarn(line)
        if (jsonLine.isEmpty) {
            // we log as info all the lines that are not valid json
            // some sources actually log their process on stdout, we
            // want to make sure this info is available in the logs.
            containerLogMdcBuilder.build().use { mdcScope -> logger.info(line) }
        }
        return jsonLine.stream()
    }

    protected fun validate(json: JsonNode): Boolean {
        val res = protocolValidator.test(json)
        if (!res) {
            logger.error("Validation failed: {}", Jsons.serialize(json))
        }
        return res
    }

    protected fun toAirbyteMessage(json: JsonNode?): Stream<AirbyteMessage> {
        val m = Jsons.tryObject(json, AirbyteMessage::class.java)
        if (m.isEmpty) {
            logger.error("Deserialization failed: {}", Jsons.serialize(json))
        }
        return m.stream()
    }

    protected fun filterLog(message: AirbyteMessage): Boolean {
        val isLog = message.type == AirbyteMessage.Type.LOG
        if (isLog) {
            containerLogMdcBuilder.build().use { mdcScope -> internalLog(message.log) }
        }
        return !isLog
    }

    protected fun internalLog(logMessage: AirbyteLogMessage) {
        val combinedMessage =
            logMessage.message +
                    (if (logMessage.stackTrace != null)
                        (System.lineSeparator() + "Stack Trace: " + logMessage.stackTrace)
                    else "")

        when (logMessage.level) {
            AirbyteLogMessage.Level.FATAL,
            AirbyteLogMessage.Level.ERROR -> logger.error(combinedMessage)
            AirbyteLogMessage.Level.WARN -> logger.warn(combinedMessage)
            AirbyteLogMessage.Level.DEBUG -> logger.debug(combinedMessage)
            AirbyteLogMessage.Level.TRACE -> logger.trace(combinedMessage)
            else -> logger.info(combinedMessage)
        }
    }

    // Human-readable byte size from
    // https://stackoverflow.com/questions/3758606/how-can-i-convert-byte-size-into-a-human-readable-format-in-java
    private fun humanReadableByteCountSI(bytes: Long): String {
        var bytes = bytes
        if (-1000 < bytes && bytes < 1000) {
            return "$bytes B"
        }
        val ci: CharacterIterator = StringCharacterIterator("kMGTPE")
        while (bytes <= -999950 || bytes >= 999950) {
            bytes /= 1000
            ci.next()
        }
        return String.format("%.1f %cB", bytes / 1000.0, ci.current())
    }
}
