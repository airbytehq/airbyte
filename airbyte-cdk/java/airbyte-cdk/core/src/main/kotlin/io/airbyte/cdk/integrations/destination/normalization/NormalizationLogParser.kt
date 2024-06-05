/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.normalization

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.AirbyteLogMessage
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.protocol.models.AirbyteTraceMessage
import java.io.*
import java.nio.charset.StandardCharsets
import java.util.stream.Stream
import org.apache.logging.log4j.util.Strings

/**
 * A simple wrapper for base-normalization logs. Reads messages off of stdin and sticks them into
 * appropriate AirbyteMessages (log or trace), then dumps those messages to stdout
 *
 * does mostly the same thing as
 * [io.airbyte.workers.normalization.NormalizationAirbyteStreamFactory]. That class is not actively
 * developed, and will be deleted after all destinations run normalization in-connector.
 *
 * Aggregates all error logs and emits them as a single trace message at the end. If the underlying
 * process emits any trace messages, they are passed through immediately.
 */
class NormalizationLogParser {
    val dbtErrors: MutableList<String> = ArrayList()

    fun create(bufferedReader: BufferedReader): Stream<AirbyteMessage> {
        return bufferedReader.lines().flatMap { line: String -> this.toMessages(line) }
    }

    @VisibleForTesting
    fun toMessages(line: String): Stream<AirbyteMessage> {
        if (Strings.isEmpty(line)) {
            return Stream.of(logMessage(AirbyteLogMessage.Level.INFO, ""))
        }
        val json = Jsons.tryDeserializeWithoutWarn(line)
        return if (json.isPresent) {
            jsonToMessage(json.get())
        } else {
            nonJsonLineToMessage(line)
        }
    }

    /**
     * Wrap the line in an AirbyteLogMessage, and do very naive dbt error log detection.
     *
     * This is needed for dbt < 1.0.0, which don't support json-format logs.
     */
    private fun nonJsonLineToMessage(line: String): Stream<AirbyteMessage> {
        // Super hacky thing to try and detect error lines
        if (line.contains("[error]")) {
            dbtErrors.add(line)
        }
        return Stream.of(logMessage(AirbyteLogMessage.Level.INFO, line))
    }

    /**
     * There are two cases here: Either the json is already an AirbyteMessage (and we should just
     * emit it without change), or it's dbt json log, and we need to do some extra work to convert
     * it to a log message + aggregate error logs.
     */
    private fun jsonToMessage(jsonLine: JsonNode): Stream<AirbyteMessage> {
        val message = Jsons.tryObject(jsonLine, AirbyteMessage::class.java)
        if (message.isPresent) {
            // This line is already an AirbyteMessage; we can just return it directly
            // (these messages come from the transform_config / transform_catalog scripts)
            return message.stream()
        } else {
            /*
             * This line is a JSON-format dbt log. We need to extract the message and wrap it in a logmessage
             * And if it's an error, we also need to collect it into dbtErrors. Example log message, formatted
             * for readability: { "code": "A001", "data": { "v": "=1.0.9" }, "invocation_id":
             * "3f9a0b9f-9623-4c25-8708-1f6ae851e738", "level": "info", "log_version": 1, "msg":
             * "Running with dbt=1.0.9", "node_info": {}, "pid": 65, "thread_name": "MainThread", "ts":
             * "2023-04-12T21:03:23.079315Z", "type": "log_line" }
             */
            val logLevel = if ((jsonLine.hasNonNull("level"))) jsonLine["level"].asText() else ""
            var logMsg = if (jsonLine.hasNonNull("msg")) jsonLine["msg"].asText() else ""
            val level: AirbyteLogMessage.Level
            when (logLevel) {
                "debug" -> level = AirbyteLogMessage.Level.DEBUG
                "info" -> level = AirbyteLogMessage.Level.INFO
                "warn" -> level = AirbyteLogMessage.Level.WARN
                "error" -> {
                    // This is also not _amazing_, but we make the assumption that all error logs
                    // should be emitted in
                    // the trace message
                    // In practice, this seems to be a valid assumption.
                    level = AirbyteLogMessage.Level.ERROR
                    dbtErrors.add(logMsg)
                }
                else -> {
                    level = AirbyteLogMessage.Level.INFO
                    logMsg = jsonLine.toPrettyString()
                }
            }
            return Stream.of(logMessage(level, logMsg))
        }
    }

    companion object {
        private fun logMessage(level: AirbyteLogMessage.Level, message: String): AirbyteMessage {
            return AirbyteMessage()
                .withType(AirbyteMessage.Type.LOG)
                .withLog(AirbyteLogMessage().withLevel(level).withMessage(message))
        }

        @JvmStatic
        fun main(args: Array<String>) {
            val normalizationLogParser = NormalizationLogParser()
            val airbyteMessageStream =
                normalizationLogParser.create(
                    BufferedReader(InputStreamReader(System.`in`, StandardCharsets.UTF_8))
                )
            airbyteMessageStream.forEachOrdered { message: AirbyteMessage ->
                println(Jsons.serialize(message))
            }

            val errors = normalizationLogParser.dbtErrors
            val dbtErrorStack = java.lang.String.join("\n", errors)
            if ("" != dbtErrorStack) {
                val errorMap =
                    SentryExceptionHelper.getUsefulErrorMessageAndTypeFromDbtError(dbtErrorStack)
                val internalMessage =
                    errorMap[SentryExceptionHelper.ErrorMapKeys.ERROR_MAP_MESSAGE_KEY]
                val traceMessage =
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.TRACE)
                        .withTrace(
                            AirbyteTraceMessage()
                                .withType(AirbyteTraceMessage.Type.ERROR)
                                .withEmittedAt(System.currentTimeMillis().toDouble())
                                .withError(
                                    AirbyteErrorTraceMessage()
                                        .withFailureType(
                                            AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR
                                        )
                                        .withMessage(
                                            "Normalization failed during the dbt run. This may indicate a problem with the data itself."
                                        )
                                        .withStackTrace("AirbyteDbtError: \n$dbtErrorStack")
                                        .withInternalMessage(internalMessage)
                                )
                        )
                println(Jsons.serialize(traceMessage))
            }
        }
    }
}
