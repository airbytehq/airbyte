/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.util.AutoCloseableIterators
import io.airbyte.commons.util.MoreIterators
import io.airbyte.protocol.models.v0.*
import io.airbyte.validation.json.JsonSchemaValidator
import java.io.*
import java.net.URI
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Path
import java.time.Instant
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
import java.util.function.Consumer
import org.apache.commons.lang3.ThreadUtils
import org.assertj.core.api.AssertionsForClassTypes
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.slf4j.Logger
import org.slf4j.LoggerFactory

internal class IntegrationRunnerTest {
    private lateinit var cliParser: IntegrationCliParser
    private lateinit var stdoutConsumer: Consumer<AirbyteMessage>
    private lateinit var destination: Destination
    private lateinit var source: Source
    private lateinit var configPath: Path
    private lateinit var configuredCatalogPath: Path
    private lateinit var statePath: Path
    private lateinit var configDir: Path

    @BeforeEach
    @Throws(IOException::class)
    fun setup() {
        cliParser = mock()
        stdoutConsumer = mock()
        destination = mock()
        source = mock()
        configDir = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "test")

        configPath = IOs.writeFile(configDir, CONFIG_FILE_NAME, CONFIG_STRING)
        configuredCatalogPath =
            IOs.writeFile(
                configDir,
                CONFIGURED_CATALOG_FILE_NAME,
                Jsons.serialize(CONFIGURED_CATALOG)
            )
        statePath = IOs.writeFile(configDir, STATE_FILE_NAME, Jsons.serialize(STATE))

        val testName = Thread.currentThread().name
        ThreadUtils.getAllThreads()
            .filter { runningThread: Thread -> !runningThread.isDaemon }
            .forEach { runningThread: Thread -> runningThread.name = testName }
    }

    @Test
    @Throws(Exception::class)
    fun testSpecSource() {
        val intConfig = IntegrationConfig.spec()
        val output = ConnectorSpecification().withDocumentationUrl(URI("https://docs.airbyte.io/"))

        Mockito.`when`(cliParser.parse(ARGS)).thenReturn(intConfig)
        Mockito.`when`(source.spec()).thenReturn(output)

        IntegrationRunner(cliParser, stdoutConsumer, null, source).run(ARGS)

        Mockito.verify(source).spec()
        Mockito.verify(stdoutConsumer)
            .accept(AirbyteMessage().withType(AirbyteMessage.Type.SPEC).withSpec(output))
    }

    @Test
    @Throws(Exception::class)
    fun testSpecDestination() {
        val intConfig = IntegrationConfig.spec()
        val output = ConnectorSpecification().withDocumentationUrl(URI("https://docs.airbyte.io/"))

        Mockito.`when`(cliParser.parse(ARGS)).thenReturn(intConfig)
        Mockito.`when`(destination.spec()).thenReturn(output)

        IntegrationRunner(cliParser, stdoutConsumer, destination, null).run(ARGS)

        Mockito.verify(destination).spec()
        Mockito.verify(stdoutConsumer)
            .accept(AirbyteMessage().withType(AirbyteMessage.Type.SPEC).withSpec(output))
    }

    @Test
    @Throws(Exception::class)
    fun testCheckSource() {
        val intConfig = IntegrationConfig.check(configPath)
        val output =
            AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage("it failed")

        Mockito.`when`(cliParser.parse(ARGS)).thenReturn(intConfig)
        Mockito.`when`(source.check(CONFIG)).thenReturn(output)

        val expectedConnSpec = Mockito.mock(ConnectorSpecification::class.java)
        Mockito.`when`(source.spec()).thenReturn(expectedConnSpec)
        Mockito.`when`(expectedConnSpec.connectionSpecification).thenReturn(CONFIG)
        val jsonSchemaValidator = Mockito.mock(JsonSchemaValidator::class.java)
        IntegrationRunner(cliParser, stdoutConsumer, null, source, jsonSchemaValidator).run(ARGS)

        Mockito.verify(source).check(CONFIG)
        Mockito.verify(stdoutConsumer)
            .accept(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                    .withConnectionStatus(output)
            )
        Mockito.verify(jsonSchemaValidator).validate(any(), any())
    }

    @Test
    @Throws(Exception::class)
    fun testCheckDestination() {
        val intConfig = IntegrationConfig.check(configPath)
        val output =
            AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage("it failed")

        Mockito.`when`(cliParser.parse(ARGS)).thenReturn(intConfig)
        Mockito.`when`(destination.check(CONFIG)).thenReturn(output)

        val expectedConnSpec = Mockito.mock(ConnectorSpecification::class.java)
        Mockito.`when`(destination.spec()).thenReturn(expectedConnSpec)
        Mockito.`when`(expectedConnSpec.connectionSpecification).thenReturn(CONFIG)

        val jsonSchemaValidator = Mockito.mock(JsonSchemaValidator::class.java)

        IntegrationRunner(cliParser, stdoutConsumer, destination, null, jsonSchemaValidator)
            .run(ARGS)

        Mockito.verify(destination).check(CONFIG)
        Mockito.verify(stdoutConsumer)
            .accept(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                    .withConnectionStatus(output)
            )
        Mockito.verify(jsonSchemaValidator).validate(any(), any())
    }

    @Test
    @Throws(Exception::class)
    fun testDiscover() {
        val intConfig = IntegrationConfig.discover(configPath)
        val output =
            AirbyteCatalog().withStreams(Lists.newArrayList(AirbyteStream().withName("oceans")))

        Mockito.`when`(cliParser.parse(ARGS)).thenReturn(intConfig)
        Mockito.`when`(source.discover(CONFIG)).thenReturn(output)

        val expectedConnSpec = Mockito.mock(ConnectorSpecification::class.java)
        Mockito.`when`(source.spec()).thenReturn(expectedConnSpec)
        Mockito.`when`(expectedConnSpec.connectionSpecification).thenReturn(CONFIG)

        val jsonSchemaValidator = Mockito.mock(JsonSchemaValidator::class.java)
        IntegrationRunner(cliParser, stdoutConsumer, null, source, jsonSchemaValidator).run(ARGS)

        Mockito.verify(source).discover(CONFIG)
        Mockito.verify(stdoutConsumer)
            .accept(AirbyteMessage().withType(AirbyteMessage.Type.CATALOG).withCatalog(output))
        Mockito.verify(jsonSchemaValidator).validate(any(), any())
    }

    @Test
    @Throws(Exception::class)
    fun testRead() {
        val intConfig = IntegrationConfig.read(configPath, configuredCatalogPath, statePath)
        val message1 =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withData(Jsons.jsonNode(ImmutableMap.of("names", "byron")))
                )
        val message2 =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withData(Jsons.jsonNode(ImmutableMap.of("names", "reginald")))
                )

        Mockito.`when`(cliParser.parse(ARGS)).thenReturn(intConfig)
        Mockito.`when`(source.read(CONFIG, CONFIGURED_CATALOG, STATE))
            .thenReturn(AutoCloseableIterators.fromIterator(MoreIterators.of(message1, message2)))

        val expectedConnSpec = Mockito.mock(ConnectorSpecification::class.java)
        Mockito.`when`(source.spec()).thenReturn(expectedConnSpec)
        Mockito.`when`(expectedConnSpec.connectionSpecification).thenReturn(CONFIG)

        val jsonSchemaValidator = Mockito.mock(JsonSchemaValidator::class.java)
        IntegrationRunner(cliParser, stdoutConsumer, null, source, jsonSchemaValidator).run(ARGS)

        // noinspection resource
        Mockito.verify(source).read(CONFIG, CONFIGURED_CATALOG, STATE)
        Mockito.verify(stdoutConsumer).accept(message1)
        Mockito.verify(stdoutConsumer).accept(message2)
        Mockito.verify(jsonSchemaValidator).validate(any(), any())
    }

    @Test
    @Throws(Exception::class)
    fun testReadException() {
        val intConfig = IntegrationConfig.read(configPath, configuredCatalogPath, statePath)
        val configErrorException = ConfigErrorException("Invalid configuration")

        Mockito.`when`(cliParser.parse(ARGS)).thenReturn(intConfig)
        Mockito.`when`(source.read(CONFIG, CONFIGURED_CATALOG, STATE))
            .thenThrow(configErrorException)

        val expectedConnSpec = Mockito.mock(ConnectorSpecification::class.java)
        Mockito.`when`(source.spec()).thenReturn(expectedConnSpec)
        Mockito.`when`(expectedConnSpec.connectionSpecification).thenReturn(CONFIG)

        val jsonSchemaValidator = Mockito.mock(JsonSchemaValidator::class.java)
        val throwable =
            AssertionsForClassTypes.catchThrowable {
                IntegrationRunner(cliParser, stdoutConsumer, null, source, jsonSchemaValidator)
                    .run(ARGS)
            }

        AssertionsForClassTypes.assertThat(throwable).isInstanceOf(ConfigErrorException::class.java)
        // noinspection resource
        Mockito.verify(source).read(CONFIG, CONFIGURED_CATALOG, STATE)
    }

    @Test
    @Throws(Exception::class)
    fun testCheckNestedException() {
        val intConfig = IntegrationConfig.check(configPath)
        val output =
            AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage("Invalid configuration")
        val configErrorException = ConfigErrorException("Invalid configuration")
        val runtimeException = RuntimeException(RuntimeException(configErrorException))

        Mockito.`when`(cliParser.parse(ARGS)).thenReturn(intConfig)
        Mockito.`when`(source.check(CONFIG)).thenThrow(runtimeException)

        val expectedConnSpec = Mockito.mock(ConnectorSpecification::class.java)
        Mockito.`when`(source.spec()).thenReturn(expectedConnSpec)
        Mockito.`when`(expectedConnSpec.connectionSpecification).thenReturn(CONFIG)
        val jsonSchemaValidator = Mockito.mock(JsonSchemaValidator::class.java)
        IntegrationRunner(cliParser, stdoutConsumer, null, source, jsonSchemaValidator).run(ARGS)

        Mockito.verify(source).check(CONFIG)
        Mockito.verify(stdoutConsumer)
            .accept(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                    .withConnectionStatus(output)
            )
        Mockito.verify(jsonSchemaValidator).validate(any(), any())
    }

    @Test
    @Throws(Exception::class)
    fun testCheckRuntimeException() {
        val intConfig = IntegrationConfig.check(configPath)
        val output =
            AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(
                    String.format(
                        ConnectorExceptionUtil.COMMON_EXCEPTION_MESSAGE_TEMPLATE,
                        "Runtime Error"
                    )
                )
        val runtimeException = RuntimeException("Runtime Error")

        Mockito.`when`(cliParser.parse(ARGS)).thenReturn(intConfig)
        Mockito.`when`(source.check(CONFIG)).thenThrow(runtimeException)

        val expectedConnSpec = Mockito.mock(ConnectorSpecification::class.java)
        Mockito.`when`(source.spec()).thenReturn(expectedConnSpec)
        Mockito.`when`(expectedConnSpec.connectionSpecification).thenReturn(CONFIG)
        val jsonSchemaValidator = Mockito.mock(JsonSchemaValidator::class.java)
        IntegrationRunner(cliParser, stdoutConsumer, null, source, jsonSchemaValidator).run(ARGS)

        Mockito.verify(source).check(CONFIG)
        Mockito.verify(stdoutConsumer)
            .accept(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                    .withConnectionStatus(output)
            )
        Mockito.verify(jsonSchemaValidator).validate(any(), any())
    }

    @Test
    @Throws(Exception::class)
    fun testWrite() {
        val intConfig = IntegrationConfig.write(configPath, configuredCatalogPath)
        val consumerMock = Mockito.mock(SerializedAirbyteMessageConsumer::class.java)
        Mockito.`when`(cliParser.parse(ARGS)).thenReturn(intConfig)
        Mockito.`when`(
                destination.getSerializedMessageConsumer(CONFIG, CONFIGURED_CATALOG, stdoutConsumer)
            )
            .thenReturn(consumerMock)

        val expectedConnSpec = Mockito.mock(ConnectorSpecification::class.java)
        Mockito.`when`(destination.spec()).thenReturn(expectedConnSpec)
        Mockito.`when`(expectedConnSpec.connectionSpecification).thenReturn(CONFIG)

        val jsonSchemaValidator = Mockito.mock(JsonSchemaValidator::class.java)

        val runner =
            Mockito.spy(
                IntegrationRunner(cliParser, stdoutConsumer, destination, null, jsonSchemaValidator)
            )
        runner.run(ARGS)

        Mockito.verify(destination)
            .getSerializedMessageConsumer(CONFIG, CONFIGURED_CATALOG, stdoutConsumer)
        Mockito.verify(jsonSchemaValidator).validate(any(), any())
    }

    @Test
    @Throws(Exception::class)
    fun testDestinationConsumerLifecycleSuccess() {
        val message1 =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withData(Jsons.deserialize("{ \"color\": \"blue\" }"))
                        .withStream(STREAM_NAME)
                        .withEmittedAt(EMITTED_AT)
                )
        val message2 =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withData(Jsons.deserialize("{ \"color\": \"yellow\" }"))
                        .withStream(STREAM_NAME)
                        .withEmittedAt(EMITTED_AT)
                )
        val stateMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage().withData(Jsons.deserialize("{ \"checkpoint\": \"1\" }"))
                )
        System.setIn(
            ByteArrayInputStream(
                """${Jsons.serialize(message1)}
${Jsons.serialize(message2)}
${Jsons.serialize(stateMessage)}""".toByteArray(
                    StandardCharsets.UTF_8
                )
            )
        )

        Mockito.mock<SerializedAirbyteMessageConsumer>(SerializedAirbyteMessageConsumer::class.java)
            .use { airbyteMessageConsumerMock ->
                IntegrationRunner.consumeWriteStream(airbyteMessageConsumerMock)
                val inOrder = Mockito.inOrder(airbyteMessageConsumerMock)
                inOrder
                    .verify(airbyteMessageConsumerMock)
                    .accept(
                        Jsons.serialize(message1),
                        Jsons.serialize(message1).toByteArray(StandardCharsets.UTF_8).size
                    )
                inOrder
                    .verify(airbyteMessageConsumerMock)
                    .accept(
                        Jsons.serialize(message2),
                        Jsons.serialize(message2).toByteArray(StandardCharsets.UTF_8).size
                    )
                inOrder
                    .verify(airbyteMessageConsumerMock)
                    .accept(
                        Jsons.serialize(stateMessage),
                        Jsons.serialize(stateMessage).toByteArray(StandardCharsets.UTF_8).size
                    )
            }
    }

    @Test
    @Throws(Exception::class)
    fun testDestinationConsumerLifecycleFailure() {
        val message1 =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withData(Jsons.deserialize("{ \"color\": \"blue\" }"))
                        .withStream(STREAM_NAME)
                        .withEmittedAt(EMITTED_AT)
                )
        val message2 =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withData(Jsons.deserialize("{ \"color\": \"yellow\" }"))
                        .withStream(STREAM_NAME)
                        .withEmittedAt(EMITTED_AT)
                )
        System.setIn(
            ByteArrayInputStream(
                """${Jsons.serialize(message1)}
${Jsons.serialize(message2)}""".toByteArray(
                    StandardCharsets.UTF_8
                )
            )
        )

        Mockito.mock<SerializedAirbyteMessageConsumer>(SerializedAirbyteMessageConsumer::class.java)
            .use { airbyteMessageConsumerMock ->
                Mockito.doThrow(IOException("error"))
                    .`when`(airbyteMessageConsumerMock)
                    .accept(
                        Jsons.serialize(message1),
                        Jsons.serialize(message1).toByteArray(StandardCharsets.UTF_8).size
                    )
                Assertions.assertThrows(IOException::class.java) {
                    IntegrationRunner.consumeWriteStream(airbyteMessageConsumerMock)
                }
                val inOrder = Mockito.inOrder(airbyteMessageConsumerMock)
                inOrder
                    .verify(airbyteMessageConsumerMock)
                    .accept(
                        Jsons.serialize(message1),
                        Jsons.serialize(message1).toByteArray(StandardCharsets.UTF_8).size
                    )
                inOrder.verifyNoMoreInteractions()
            }
    }

    @Test
    fun testInterruptOrphanThread() {
        val caughtExceptions: MutableList<Exception> = ArrayList()
        startSleepingThread(caughtExceptions, false)
        IntegrationRunner.stopOrphanedThreads(
            { Assertions.fail() },
            3,
            TimeUnit.SECONDS,
            10,
            TimeUnit.SECONDS
        )
        try {
            TimeUnit.SECONDS.sleep(15)
        } catch (e: Exception) {
            throw RuntimeException(e)
        }
        val runningThreads =
            ThreadUtils.getAllThreads().filter(IntegrationRunner::filterOrphanedThread)

        // all threads should be interrupted
        Assertions.assertEquals(listOf<Any>(), runningThreads)
        Assertions.assertEquals(1, caughtExceptions.size)
    }

    @Test
    fun testNoInterruptOrphanThread() {
        val caughtExceptions: MutableList<Exception> = ArrayList()
        val exitCalled = AtomicBoolean(false)
        startSleepingThread(caughtExceptions, true)
        IntegrationRunner.stopOrphanedThreads(
            { exitCalled.set(true) },
            3,
            TimeUnit.SECONDS,
            10,
            TimeUnit.SECONDS
        )
        try {
            TimeUnit.SECONDS.sleep(15)
        } catch (e: Exception) {
            throw RuntimeException(e)
        }

        val runningThreads =
            ThreadUtils.getAllThreads().filter(IntegrationRunner::filterOrphanedThread)

        // a thread that refuses to be interrupted should remain
        Assertions.assertEquals(1, runningThreads.size)
        Assertions.assertEquals(1, caughtExceptions.size)
        Assertions.assertTrue(exitCalled.get())
    }

    private fun startSleepingThread(
        caughtExceptions: MutableList<Exception>,
        ignoreInterrupt: Boolean
    ) {
        val executorService =
            Executors.newFixedThreadPool(1) { r: Runnable ->
                // Create a thread that should be identified as orphaned if still running during
                // shutdown
                val thread = Thread(r)
                thread.name = "sleeping-thread"
                thread.isDaemon = false
                thread
            }
        executorService.submit {
            for (tries in 0..2) {
                try {
                    TimeUnit.MINUTES.sleep(5)
                } catch (e: Exception) {
                    LOGGER.info("Caught Exception", e)
                    caughtExceptions.add(e)
                    if (!ignoreInterrupt) {
                        executorService.shutdownNow()
                        break
                    }
                }
            }
        }
    }

    @Test
    fun testParseConnectorImage() {
        Assertions.assertEquals("unknown", IntegrationRunner.parseConnectorVersion(null))
        Assertions.assertEquals("unknown", IntegrationRunner.parseConnectorVersion(""))
        Assertions.assertEquals(
            "1.0.1-alpha",
            IntegrationRunner.parseConnectorVersion("airbyte/destination-test:1.0.1-alpha")
        )
        Assertions.assertEquals(
            "dev",
            IntegrationRunner.parseConnectorVersion("airbyte/destination-test:dev")
        )
        Assertions.assertEquals(
            "1.0.1-alpha",
            IntegrationRunner.parseConnectorVersion("destination-test:1.0.1-alpha")
        )
        Assertions.assertEquals(
            "1.0.1-alpha",
            IntegrationRunner.parseConnectorVersion(":1.0.1-alpha")
        )
    }

    @Test
    fun testConsumptionOfInvalidStateMessage() {
        val invalidStateMessage =
            """
                                       {
                                         "type" : "STATE",
                                         "state" : {
                                           "type": "NOT_RECOGNIZED",
                                           "global": {
                                             "streamStates": {
                                               "foo" : "bar"
                                             }
                                           }
                                         }
                                       }
                                       
                                       """.trimIndent()

        Assertions.assertThrows(IllegalStateException::class.java) {
            Mockito.mock(AirbyteMessageConsumer::class.java).use { consumer ->
                Destination.ShimToSerializedAirbyteMessageConsumer.consumeMessage(
                    consumer,
                    invalidStateMessage
                )
            }
        }
    }

    @Test
    fun testConsumptionOfInvalidNonStateMessage() {
        val invalidNonStateMessage =
            """
                                          {
                                            "type" : "NOT_RECOGNIZED",
                                            "record" : {
                                              "namespace": "namespace",
                                              "stream": "stream",
                                              "emittedAt": 123456789
                                            }
                                          }
                                          
                                          """.trimIndent()

        Assertions.assertDoesNotThrow {
            Mockito.mock<AirbyteMessageConsumer>(AirbyteMessageConsumer::class.java).use { consumer
                ->
                Destination.ShimToSerializedAirbyteMessageConsumer.consumeMessage(
                    consumer,
                    invalidNonStateMessage
                )
                Mockito.verify(consumer, Mockito.times(0)).accept(any<AirbyteMessage>())
            }
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(IntegrationRunnerTest::class.java)

        private const val CONFIG_FILE_NAME = "config.json"
        private const val CONFIGURED_CATALOG_FILE_NAME = "configured_catalog.json"
        private const val STATE_FILE_NAME = "state.json"

        private val ARGS = arrayOf("args")

        private const val CONFIG_STRING = "{ \"username\": \"airbyte\" }"
        private val CONFIG: JsonNode = Jsons.deserialize(CONFIG_STRING)
        private const val STREAM_NAME = "users"
        private val EMITTED_AT = Instant.now().toEpochMilli()
        private val TEST_ROOT: Path = Path.of("/tmp/airbyte_tests")

        private val CATALOG: AirbyteCatalog =
            AirbyteCatalog().withStreams(Lists.newArrayList(AirbyteStream().withName(STREAM_NAME)))
        private val CONFIGURED_CATALOG: ConfiguredAirbyteCatalog =
            CatalogHelpers.toDefaultConfiguredCatalog(CATALOG)
        private val STATE: JsonNode = Jsons.jsonNode(ImmutableMap.of("checkpoint", "05/08/1945"))
    }
}
