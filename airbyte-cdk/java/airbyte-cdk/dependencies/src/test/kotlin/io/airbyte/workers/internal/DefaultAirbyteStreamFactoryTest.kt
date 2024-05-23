/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.internal

import io.airbyte.commons.json.Jsons
import io.airbyte.commons.logging.MdcScope
import io.airbyte.protocol.models.AirbyteLogMessage
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.workers.test_utils.AirbyteMessageUtils
import java.io.BufferedReader
import java.io.ByteArrayInputStream
import java.io.InputStream
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets
import java.util.*
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers
import org.mockito.Mockito
import org.slf4j.Logger

internal class DefaultAirbyteStreamFactoryTest {
    private lateinit var protocolPredicate: AirbyteProtocolPredicate
    private lateinit var logger: Logger

    @BeforeEach
    fun setup() {
        protocolPredicate = Mockito.mock(AirbyteProtocolPredicate::class.java)
        Mockito.`when`(protocolPredicate.test(ArgumentMatchers.any())).thenReturn(true)
        logger = Mockito.mock(Logger::class.java)
    }

    @Test
    fun testValid() {
        val record1 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green")

        val messageStream = stringToMessageStream(Jsons.serialize(record1))
        val expectedStream = Stream.of(record1)

        Assertions.assertEquals(expectedStream.toList(), messageStream.toList())
        Mockito.verifyNoInteractions(logger)
    }

    @Test
    fun testLoggingLine() {
        val invalidRecord = "invalid line"

        val messageStream = stringToMessageStream(invalidRecord)

        Assertions.assertEquals(emptyList<Any>(), messageStream.toList())
        Mockito.verify(logger).info(ArgumentMatchers.anyString())
        Mockito.verifyNoMoreInteractions(logger)
    }

    @Test
    fun testLoggingLevel() {
        val logMessage =
            AirbyteMessageUtils.createLogMessage(AirbyteLogMessage.Level.WARN, "warning")

        val messageStream = stringToMessageStream(Jsons.serialize(logMessage))

        Assertions.assertEquals(emptyList<Any>(), messageStream.toList())
        Mockito.verify(logger).warn("warning")
        Mockito.verifyNoMoreInteractions(logger)
    }

    @Test
    fun testFailValidation() {
        val invalidRecord = "{ \"fish\": \"tuna\"}"

        Mockito.`when`(protocolPredicate!!.test(Jsons.deserialize(invalidRecord))).thenReturn(false)

        val messageStream = stringToMessageStream(invalidRecord)

        Assertions.assertEquals(emptyList<Any>(), messageStream.toList())
        Mockito.verify(logger).error(ArgumentMatchers.anyString(), ArgumentMatchers.anyString())
        Mockito.verifyNoMoreInteractions(logger)
    }

    @Test
    fun testFailDeserialization() {
        val invalidRecord = "{ \"type\": \"abc\"}"

        Mockito.`when`(protocolPredicate!!.test(Jsons.deserialize(invalidRecord))).thenReturn(true)

        val messageStream = stringToMessageStream(invalidRecord)

        Assertions.assertEquals(emptyList<Any>(), messageStream.toList())
        Mockito.verify(logger).error(ArgumentMatchers.anyString(), ArgumentMatchers.anyString())
        Mockito.verifyNoMoreInteractions(logger)
    }

    @Test
    fun testFailsSize() {
        val record1 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green")

        val inputStream: InputStream =
            ByteArrayInputStream(record1.toString().toByteArray(StandardCharsets.UTF_8))
        val bufferedReader = BufferedReader(InputStreamReader(inputStream, StandardCharsets.UTF_8))

        val messageStream =
            DefaultAirbyteStreamFactory(
                    protocolPredicate,
                    logger,
                    MdcScope.Builder(),
                    Optional.of(RuntimeException::class.java),
                    1L
                )
                .create(bufferedReader)

        Assertions.assertThrows(RuntimeException::class.java) { messageStream.toList() }
    }

    @Test
    @Disabled
    fun testMissingNewLineBetweenValidRecords() {
        val record1 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green")
        val record2 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "yellow")

        val inputString = Jsons.serialize(record1) + Jsons.serialize(record2)

        val messageStream = stringToMessageStream(inputString)

        Assertions.assertEquals(emptyList<Any>(), messageStream.toList())
        Mockito.verify(logger).error(ArgumentMatchers.anyString(), ArgumentMatchers.anyString())
        Mockito.verifyNoMoreInteractions(logger)
    }

    private fun stringToMessageStream(inputString: String): Stream<AirbyteMessage> {
        val inputStream: InputStream =
            ByteArrayInputStream(inputString.toByteArray(StandardCharsets.UTF_8))
        val bufferedReader = BufferedReader(InputStreamReader(inputStream, StandardCharsets.UTF_8))
        return DefaultAirbyteStreamFactory(
                protocolPredicate,
                logger,
                MdcScope.Builder(),
                Optional.empty()
            )
            .create(bufferedReader)
    }

    companion object {
        private const val STREAM_NAME = "user_preferences"
        private const val FIELD_NAME = "favorite_color"
    }
}
