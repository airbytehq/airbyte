/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import io.airbyte.cdk.integrations.util.ConnectorExceptionHandler
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.protocol.models.AirbyteTraceMessage
import java.io.*
import java.nio.charset.StandardCharsets
import java.util.*
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.function.Executable
import org.mockito.Mockito

class AirbyteExceptionHandlerTest {
    var originalOut: PrintStream = System.out
    private val outContent = ByteArrayOutputStream()
    private lateinit var airbyteExceptionHandler: AirbyteExceptionHandler

    @BeforeEach
    fun setup() {
        System.setOut(PrintStream(outContent, true, StandardCharsets.UTF_8))

        // mocking terminate() method in AirbyteExceptionHandler, so we don't kill the JVM
        airbyteExceptionHandler = Mockito.spy(AirbyteExceptionHandler())
        Mockito.doNothing().`when`(airbyteExceptionHandler).terminate()

        AirbyteExceptionHandler.addThrowableForDeinterpolation(RuntimeException::class.java)
    }

    @Test
    @Throws(Exception::class)
    fun testTraceMessageEmission() {
        runTestWithMessage("error")

        val traceMessage = findFirstTraceMessage()
        Assertions.assertAll(
            Executable {
                Assertions.assertEquals(AirbyteTraceMessage.Type.ERROR, traceMessage.trace.type)
            },
            Executable {
                Assertions.assertEquals(
                    AirbyteExceptionHandler.logMessage,
                    traceMessage.trace.error.message
                )
            },
            Executable {
                Assertions.assertEquals(
                    AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR,
                    traceMessage.trace.error.failureType
                )
            }
        )
    }

    @Test
    @Throws(Exception::class)
    fun testMessageDeinterpolation() {
        AirbyteExceptionHandler.addStringForDeinterpolation("foo")
        AirbyteExceptionHandler.addStringForDeinterpolation("bar")

        // foo and bar are added to the list explicitly
        // name and description are added implicitly by the exception handler.
        // all of them should be replaced by '?'
        // (including FOO, which should be detected case-insensitively)
        runTestWithMessage("Error happened in arst_FOO_bar_zxcv (name: description)")

        val traceMessage = findFirstTraceMessage()
        Assertions.assertAll(
            Executable {
                Assertions.assertEquals(AirbyteTraceMessage.Type.ERROR, traceMessage.trace.type)
            },
            Executable {
                Assertions.assertEquals(
                    "Error happened in arst_FOO_bar_zxcv (name: description)",
                    traceMessage.trace.error.message
                )
            },
            Executable {
                Assertions.assertEquals(
                    "Error happened in arst_?_?_zxcv (?: ?)",
                    traceMessage.trace.error.internalMessage
                )
            },
            Executable {
                Assertions.assertEquals(
                    AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR,
                    traceMessage.trace.error.failureType
                )
            },
            Executable {
                Assertions.assertNull(
                    traceMessage.trace.error.stackTrace,
                    "Stacktrace should be null if deinterpolating the error message"
                )
            }
        )
    }

    /**
     * We should only deinterpolate whole words, i.e. if the target string is not adjacent to an
     * alphanumeric character.
     */
    @Test
    @Throws(Exception::class)
    fun testMessageSmartDeinterpolation() {
        AirbyteExceptionHandler.addStringForDeinterpolation("foo")
        AirbyteExceptionHandler.addStringForDeinterpolation("bar")

        runTestWithMessage("Error happened in foobar")

        val traceMessage = findFirstTraceMessage()
        // We shouldn't deinterpolate at all in this case, so we will get the default trace message
        // behavior.
        Assertions.assertAll(
            Executable {
                Assertions.assertEquals(
                    AirbyteExceptionHandler.logMessage,
                    traceMessage.trace.error.message
                )
            },
            Executable {
                Assertions.assertEquals(
                    "java.lang.RuntimeException: Error happened in foobar",
                    traceMessage.trace.error.internalMessage
                )
            }
        )
    }

    /**
     * When one of the target strings is a substring of another, we should not deinterpolate the
     * substring.
     */
    @Test
    @Throws(Exception::class)
    fun testMessageSubstringDeinterpolation() {
        AirbyteExceptionHandler.addStringForDeinterpolation("airbyte")
        AirbyteExceptionHandler.addStringForDeinterpolation("airbyte_internal")

        runTestWithMessage("Error happened in airbyte_internal.foo")

        val traceMessage = findFirstTraceMessage()
        Assertions.assertEquals("Error happened in ?.foo", traceMessage.trace.error.internalMessage)
    }

    /** We should only deinterpolate specific exception classes. */
    @Test
    @Throws(Exception::class)
    fun testClassDeinterpolation() {
        AirbyteExceptionHandler.addStringForDeinterpolation("foo")

        runTestWithMessage(IOException("Error happened in foo"))

        val traceMessage = findFirstTraceMessage()
        // We shouldn't deinterpolate at all in this case, so we will get the default trace message
        // behavior.
        Assertions.assertAll(
            Executable {
                Assertions.assertEquals(
                    AirbyteExceptionHandler.logMessage,
                    traceMessage.trace.error.message
                )
            },
            Executable {
                Assertions.assertEquals(
                    "java.io.IOException: Error happened in foo",
                    traceMessage.trace.error.internalMessage
                )
            }
        )
    }

    /** We should check the classes of the entire exception chain, not just the root exception. */
    @Test
    @Throws(Exception::class)
    fun testNestedThrowableClassDeinterpolation() {
        AirbyteExceptionHandler.addStringForDeinterpolation("foo")

        runTestWithMessage(Exception(RuntimeException("Error happened in foo")))

        val traceMessage = findFirstTraceMessage()
        // We shouldn't deinterpolate at all in this case, so we will get the default trace message
        // behavior.
        Assertions.assertEquals("Error happened in ?", traceMessage.trace.error.internalMessage)
    }

    @Throws(InterruptedException::class)
    private fun runTestWithMessage(message: String) {
        runTestWithMessage(RuntimeException(message))
    }

    @Throws(InterruptedException::class)
    private fun runTestWithMessage(throwable: Throwable) {
        // have to spawn a new thread to test the uncaught exception handling,
        // because junit catches any exceptions in main thread, i.e. they're not 'uncaught'
        val thread: Thread =
            object : Thread() {
                override fun run() {
                    val runner = Mockito.mock(IntegrationRunner::class.java)
                    val exceptionHandler = ConnectorExceptionHandler()
                    Mockito.doThrow(throwable)
                        .`when`(runner)
                        .run(arrayOf("write"), exceptionHandler)
                    runner.run(arrayOf("write"), exceptionHandler)
                }
            }
        thread.uncaughtExceptionHandler = airbyteExceptionHandler
        thread.start()
        thread.join()
        System.out.flush()
    }

    @AfterEach
    fun teardown() {
        System.setOut(originalOut)

        AirbyteExceptionHandler.STRINGS_TO_DEINTERPOLATE.clear()
        AirbyteExceptionHandler.addCommonStringsToDeinterpolate()

        AirbyteExceptionHandler.THROWABLES_TO_DEINTERPOLATE.clear()
    }

    private fun findFirstTraceMessage(): AirbyteMessage {
        val maybeTraceMessage =
            Arrays.stream(
                    outContent
                        .toString(StandardCharsets.UTF_8)
                        .split("\n".toRegex())
                        .dropLastWhile { it.isEmpty() }
                        .toTypedArray()
                )
                .map { line: String ->
                    // these tests sometimes emit non-json stdout (e.g. log4j warnings)
                    // so we try-catch to handle those malformed lines.
                    try {
                        return@map Jsons.deserialize<AirbyteMessage>(
                            line,
                            AirbyteMessage::class.java
                        )
                    } catch (e: Exception) {
                        return@map null
                    }
                }
                .filter { message: AirbyteMessage? ->
                    message != null && message.type == AirbyteMessage.Type.TRACE
                }
                .findFirst()
        Assertions.assertTrue(
            maybeTraceMessage.isPresent,
            "Expected to find a trace message in stdout"
        )
        return maybeTraceMessage.get()
    }
}
