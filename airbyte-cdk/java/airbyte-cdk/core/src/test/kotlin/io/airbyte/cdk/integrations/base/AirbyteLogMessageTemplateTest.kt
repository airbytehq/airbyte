/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.AirbyteLogMessage
import io.airbyte.protocol.models.AirbyteMessage
import java.io.*
import java.nio.charset.StandardCharsets
import java.util.regex.Pattern
import org.apache.logging.log4j.Level
import org.apache.logging.log4j.core.LoggerContext
import org.apache.logging.log4j.core.appender.OutputStreamAppender
import org.apache.logging.log4j.core.config.Configurator
import org.apache.logging.log4j.core.config.LoggerConfig
import org.apache.logging.log4j.spi.ExtendedLogger
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource
import org.junit.platform.commons.util.StringUtils

class AirbyteLogMessageTemplateTest {
    private lateinit var loggerContext: LoggerContext
    private lateinit var rootLoggerConfig: LoggerConfig
    private lateinit var logger: ExtendedLogger
    private lateinit var outputStreamAppender: OutputStreamAppender
    private lateinit var outputContent: ByteArrayOutputStream

    fun getLogger() {
        // We are creating a log appender with the same output pattern
        // as the console json appender defined in this project's log4j2.xml file.
        // We then attach this log appender with the LOGGER instance so that we can validate the
        // logs
        // produced by code and assert that it matches the expected format.
        loggerContext = Configurator.initialize(null, "log4j2.xml")

        val configuration = loggerContext.configuration
        rootLoggerConfig = configuration.getLoggerConfig("")

        outputContent = ByteArrayOutputStream()
        outputStreamAppender =
            OutputStreamAppender.createAppender(
                rootLoggerConfig.appenders[CONSOLE_JSON_APPENDER]!!.layout,
                null,
                outputContent,
                OUTPUT_STREAM_APPENDER,
                false,
                true
            )
        outputStreamAppender.start()

        rootLoggerConfig.addAppender(outputStreamAppender, Level.ALL, null)
        logger = loggerContext.getLogger(AirbyteLogMessageTemplateTest::class.java)
    }

    @AfterEach
    fun closeLogger() {
        outputStreamAppender.stop()
        rootLoggerConfig.removeAppender(OUTPUT_STREAM_APPENDER)
        loggerContext.close()
    }

    @Test
    @Throws(IOException::class)
    fun testAirbyteLogMessageFormat() {
        getLogger()
        logger.info("hello")

        outputContent.flush()
        val logMessage = outputContent.toString(StandardCharsets.UTF_8)
        val airbyteMessage = validateLogIsAirbyteMessage(logMessage)
        val airbyteLogMessage = validateAirbyteMessageIsLog(airbyteMessage)

        val connectorLogMessage = airbyteLogMessage.message
        // validate that the message inside AirbyteLogMessage matches the pattern.
        // pattern to check for is: LOG_LEVEL className(methodName):LineNumber logMessage
        val connectorLogMessageRegex =
            String.format(
                "^INFO %s [\\w+.]*.AirbyteLogMessageTemplateTest\\(testAirbyteLogMessageFormat\\):\\d+ hello$",
                Pattern.compile(Thread.currentThread().name)
            )
        val pattern = Pattern.compile(connectorLogMessageRegex)

        val matcher = pattern.matcher(connectorLogMessage)
        Assertions.assertTrue(matcher.matches(), connectorLogMessage)
    }

    private fun validateLogIsAirbyteMessage(logMessage: String): AirbyteMessage {
        val jsonLine = Jsons.tryDeserialize(logMessage)
        Assertions.assertFalse(jsonLine.isEmpty)

        val m = Jsons.tryObject(jsonLine.get(), AirbyteMessage::class.java)
        Assertions.assertFalse(m.isEmpty)
        return m.get()
    }

    private fun validateAirbyteMessageIsLog(airbyteMessage: AirbyteMessage): AirbyteLogMessage {
        Assertions.assertEquals(AirbyteMessage.Type.LOG, airbyteMessage.type)
        Assertions.assertNotNull(airbyteMessage.log)
        Assertions.assertFalse(StringUtils.isBlank(airbyteMessage.log.message))
        return airbyteMessage.log
    }

    @ParameterizedTest
    @ValueSource(ints = [2, 100, 9000])
    @Throws(IOException::class)
    fun testAirbyteLogMessageLength(stringRepetitions: Int) {
        getLogger()
        val sb = StringBuilder()
        for (i in 0 until stringRepetitions) {
            sb.append("abcd")
        }
        logger.info(sb.toString(), RuntimeException("aaaaa bbbbbb ccccccc dddddd"))
        outputContent.flush()
        val logMessage = outputContent.toString(StandardCharsets.UTF_8)

        val airbyteMessage = validateLogIsAirbyteMessage(logMessage)
        val airbyteLogMessage = validateAirbyteMessageIsLog(airbyteMessage)
        val connectorLogMessage = airbyteLogMessage.message

        // #30781 - message length is capped at 16,000 charcters.
        val j = connectorLogMessage.length
        Assertions.assertFalse(connectorLogMessage.length > 16001)
        Assertions.assertTrue(logMessage.length < 32768)
    }

    companion object {
        const val OUTPUT_STREAM_APPENDER: String = "OutputStreamAppender"
        const val CONSOLE_JSON_APPENDER: String = "ConsoleJSONAppender"
    }
}
