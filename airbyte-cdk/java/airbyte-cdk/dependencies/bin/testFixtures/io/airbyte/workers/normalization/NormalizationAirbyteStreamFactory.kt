/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.normalization

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeType
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.logging.MdcScope
import io.airbyte.protocol.models.AirbyteLogMessage
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.workers.internal.AirbyteStreamFactory
import io.github.oshai.kotlinlogging.KLogger
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.BufferedReader
import java.util.stream.Stream

private val LOGGER = KotlinLogging.logger {}
/**
 * Creates a stream from an input stream. The produced stream attempts to parse each line of the
 * InputStream into a AirbyteMessage. If the line cannot be parsed into a AirbyteMessage it is
 * assumed to be from dbt. dbt [error] messages are also parsed
 *
 * If a line starts with a AirbyteMessage and then has other characters after it, that
 * AirbyteMessage will still be parsed. If there are multiple AirbyteMessage records on the same
 * line, only the first will be parsed.
 */
class NormalizationAirbyteStreamFactory
internal constructor(
    private val logger: KLogger,
    private val containerLogMdcBuilder: MdcScope.Builder
) : AirbyteStreamFactory {
    val dbtErrors: MutableList<String> = ArrayList()

    constructor(containerLogMdcBuilder: MdcScope.Builder) : this(LOGGER, containerLogMdcBuilder)

    override fun create(bufferedReader: BufferedReader): Stream<AirbyteMessage> {
        return bufferedReader
            .lines()
            .flatMap { line: String -> this.filterOutAndHandleNonJsonLines(line) }
            .flatMap { jsonLine: JsonNode ->
                this.filterOutAndHandleNonAirbyteMessageLines(jsonLine)
            } // so now we are just left with AirbyteMessages
            .filter { airbyteMessage: AirbyteMessage ->
                val isLog = airbyteMessage!!.type == AirbyteMessage.Type.LOG
                if (isLog) {
                    containerLogMdcBuilder.build().use { mdcScope ->
                        internalLog(airbyteMessage.log)
                    }
                }
                !isLog
            }
    }

    private fun filterOutAndHandleNonJsonLines(line: String): Stream<JsonNode> {
        val jsonLine = Jsons.tryDeserialize(line)
        if (jsonLine.isEmpty) {
            // we log as info all the lines that are not valid json.
            containerLogMdcBuilder.build().use { mdcScope ->
                logger.info(line)
                // this is really hacky and vulnerable to picking up lines we don't want,
                // however it is only for destinations that are using dbt version < 1.0.
                // For v1 + we switch on JSON logging and parse those in the next block.
                if (line.contains("[error]")) {
                    dbtErrors.add(line)
                }
            }
        }
        return jsonLine.stream()
    }

    private fun filterOutAndHandleNonAirbyteMessageLines(
        jsonLine: JsonNode
    ): Stream<AirbyteMessage> {
        val m = Jsons.tryObject(jsonLine, AirbyteMessage::class.java)
        if (m.isEmpty) {
            // valid JSON but not an AirbyteMessage, so we assume this is a dbt json log
            try {
                val logLevel =
                    if ((jsonLine.nodeType == JsonNodeType.NULL || jsonLine["level"].isNull)) ""
                    else jsonLine["level"].asText()
                val logMsg = if (jsonLine["msg"].isNull) "" else jsonLine["msg"].asText()
                containerLogMdcBuilder.build().use { mdcScope ->
                    when (logLevel) {
                        "debug" -> logger.debug(logMsg)
                        "info" -> logger.info(logMsg)
                        "warn" -> logger.warn(logMsg)
                        "error" -> logAndCollectErrorMessage(logMsg)
                        else -> logger.info(jsonLine.toPrettyString())
                    }
                }
            } catch (e: Exception) {
                logger.info(jsonLine.toPrettyString())
            }
        }
        return m.stream()
    }

    private fun logAndCollectErrorMessage(logMsg: String) {
        logger.error(logMsg)
        dbtErrors.add(logMsg)
    }

    private fun internalLog(logMessage: AirbyteLogMessage) {
        when (logMessage.level) {
            AirbyteLogMessage.Level.FATAL,
            AirbyteLogMessage.Level.ERROR -> logger.error(logMessage.message)
            AirbyteLogMessage.Level.WARN -> logger.warn(logMessage.message)
            AirbyteLogMessage.Level.DEBUG -> logger.debug(logMessage.message)
            AirbyteLogMessage.Level.TRACE -> logger.trace(logMessage.message)
            else -> logger.info(logMessage.message)
        }
    }
}
