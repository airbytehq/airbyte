/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read

import com.mongodb.MongoChangeStreamException
import com.mongodb.MongoCommandException
import com.mongodb.MongoSocketReadTimeoutException
import com.mongodb.MongoTimeoutException
import com.mongodb.ServerAddress
import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.ConnectorError
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.SystemError
import io.airbyte.cdk.output.TransientError
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.net.SocketTimeoutException
import org.bson.BsonDocument
import org.bson.BsonInt32
import org.bson.BsonString
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

/**
 * Classification through the CDK's [ExceptionHandler], i.e. every classifier in order: driver
 * failures a retry from the checkpoint recovers from are transient, the message rules of
 * `application.yml` keep the configuration errors, and CHECK reports a configuration error for
 * anything.
 */
@MicronautTest
class MongoDbExceptionClassifierTest {

    @Inject lateinit var handler: ExceptionHandler

    @ParameterizedTest(name = "{0} {1}")
    @CsvSource(
        "10107, NotWritablePrimary",
        "189, PrimarySteppedDown",
        "11600, InterruptedAtShutdown",
        "91, ShutdownInProgress",
        "13436, NotPrimaryOrSecondary",
        "43, CursorNotFound",
        "262, ExceededTimeLimit",
    )
    fun testReplicaSetAndCursorServerErrorsAreTransient(code: Int, codeName: String) {
        val result: ConnectorError =
            handler.classify(RuntimeException("read failed", commandException(code, codeName)))
        Assertions.assertInstanceOf(TransientError::class.java, result, result.toString())
        Assertions.assertTrue((result as TransientError).displayMessage.contains(codeName))
    }

    @Test
    fun testSocketReadTimeoutIsTransient() {
        val exception =
            MongoSocketReadTimeoutException(
                "Timeout while receiving message",
                ServerAddress("mongo", 27017),
                SocketTimeoutException("Read timed out"),
            )
        Assertions.assertInstanceOf(TransientError::class.java, handler.classify(exception))
    }

    @Test
    fun testServerSelectionTimeoutIsTransientInReadButConfigInCheck() {
        val exception =
            MongoTimeoutException(
                "Timed out while waiting for a server that matches ReadPreferenceServerSelector{readPreference=primary}",
            )
        Assertions.assertInstanceOf(TransientError::class.java, handler.classify(exception))
        val (trace, status) = handler.handleCheckFailure(exception)
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            trace.failureType,
        )
        Assertions.assertTrue(
            status.message.contains("Timed out while waiting for a server"),
            status.message,
        )
    }

    @Test
    fun testUnauthorizedIsAConfigError() {
        val result: ConnectorError = handler.classify(commandException(13, "Unauthorized"))
        Assertions.assertInstanceOf(ConfigError::class.java, result, result.toString())
        val message = (result as ConfigError).displayMessage
        Assertions.assertTrue(message.contains("not authorized to read"), message)
    }

    /** A change stream on a standalone server: the first thing such a user sees after CHECK. */
    @Test
    fun testChangeStreamOnAStandaloneServerIsAnActionableConfigError() {
        val result: ConnectorError = handler.classify(commandException(40573, "Location40573"))
        Assertions.assertInstanceOf(ConfigError::class.java, result, result.toString())
        val message = (result as ConfigError).displayMessage
        Assertions.assertTrue(message.contains("standalone server"), message)
        Assertions.assertTrue(message.contains("Full Refresh"), message)
    }

    /** The server's own label wins over the code set, whatever the code. */
    @Test
    fun testResumableChangeStreamErrorLabelIsTransientForAnyCode() {
        val labelled =
            MongoCommandException(
                BsonDocument("ok", BsonInt32(0))
                    .append("code", BsonInt32(99999))
                    .append("codeName", BsonString("Whatever"))
                    .append("errmsg", BsonString("labelled"))
                    .append(
                        "errorLabels",
                        org.bson.BsonArray(listOf(BsonString("ResumableChangeStreamError"))),
                    ),
                ServerAddress("mongo", 27017),
            )
        Assertions.assertInstanceOf(TransientError::class.java, handler.classify(labelled))
        Assertions.assertInstanceOf(
            TransientError::class.java,
            handler.classify(commandException(175, "QueryPlanKilled")),
        )
    }

    @Test
    fun testBsonObjectTooLargeIsAnActionableConfigError() {
        val result: ConnectorError = handler.classify(commandException(10334, "BSONObjectTooLarge"))
        Assertions.assertInstanceOf(ConfigError::class.java, result, result.toString())
        val message = (result as ConfigError).displayMessage
        Assertions.assertTrue(message.contains("exceeds the 16MB BSON size limit"), message)
        Assertions.assertTrue(message.contains("'Full Refresh' sync mode"), message)
    }

    @Test
    fun testAuthenticationFailureKeepsLegacyMessage() {
        val exception =
            RuntimeException(
                "com.mongodb.MongoSecurityException: Exception authenticating " +
                    "MongoCredential{mechanism=SCRAM-SHA-256, userName='root', source='admin'}",
            )
        Assertions.assertEquals(
            "Authentication failed.  Please check the source's configured credentials.",
            (handler.classify(exception) as ConfigError).displayMessage,
        )
    }

    @Test
    fun testOtherFailuresAreSystemErrors() {
        Assertions.assertInstanceOf(
            SystemError::class.java,
            handler.classify(RuntimeException("something else")),
        )
        Assertions.assertInstanceOf(
            SystemError::class.java,
            handler.classify(MongoChangeStreamException("Cannot resume change stream")),
        )
    }

    private fun commandException(code: Int, codeName: String): MongoCommandException =
        MongoCommandException(
            BsonDocument("ok", BsonInt32(0))
                .append("code", BsonInt32(code))
                .append("codeName", BsonString(codeName))
                .append("errmsg", BsonString("$codeName from the server")),
            ServerAddress("mongo", 27017),
        )
}
