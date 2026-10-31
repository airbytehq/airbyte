/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.DefaultExceptionClassifier
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.JdbcExceptionClassifier
import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.RegexExceptionClassifierRule
import io.airbyte.cdk.output.TransientError
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest
class MySqlExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Inject lateinit var exceptionHandler: ExceptionHandler

    @Test
    fun testEofCannotReadResponse() {
        val exception =
            RuntimeException(
                "java.io.EOFException: Can not read response from server. " +
                    "Expected to read 10 bytes, read 5 bytes before connection was unexpectedly lost.",
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testEofCannotReadResponseWithThousandsSeparators() {
        val exception =
            RuntimeException(
                "java.sql.SQLException: Error retrieving record: Unexpected Exception: java.io.EOFException message given: " +
                    "Can not read response from server. Expected to read 65,568 bytes, read 40,166 bytes before connection was unexpectedly lost.",
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testEofExpectedBytesReceivedOnly() {
        val exception =
            RuntimeException("java.io.EOFException: Expected 252 bytes, received only 227 bytes")
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testEofExpectedBytesReceivedOnlyWithThousandsSeparators() {
        val exception =
            RuntimeException(
                "java.io.EOFException: Expected 65,568 bytes, received only 40,166 bytes",
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testEofFailedToReadRemaining() {
        val exception =
            RuntimeException(
                "java.io.EOFException: Failed to read remaining 2 of 2 bytes from position 114. " +
                    "Block length: 0. Initial block length: 2.",
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testEofFailedToReadNextByte() {
        val exception =
            RuntimeException("java.io.EOFException: Failed to read next byte from position 9093464")
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
        val transient = result as TransientError
        Assertions.assertTrue(
            transient.displayMessage.contains("communication issue"),
            "Expected message about communication issue, got: ${transient.displayMessage}",
        )
    }

    @Test
    fun testChangeEventProducerWithoutKnownCauseStaysConfig() {
        val exception =
            RuntimeException(
                "java.lang.RuntimeException: org.apache.kafka.connect.errors.ConnectException: " +
                    "An exception occurred in the change event producer. This connector will be stopped.",
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
    }

    @Test
    fun testChangeEventProducerWrappingEofClassifiesAsTransient() {
        // Simulates the real exception chain: ConnectException wrapping an EOFException.
        // The EOF rule precedes the generic change event producer rule, so the nested cause
        // is matched first and the failure is retried instead of surfacing as a config error.
        val eofException = java.io.EOFException("Failed to read next byte from position 9093464")
        val debeziumException = RuntimeException("Failed to deserialize data", eofException)
        val connectException =
            RuntimeException(
                "An exception occurred in the change event producer. This connector will be stopped.",
                debeziumException,
            )
        val result = classifier.classify(connectException)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testSchemaErrorStillClassifiedAsConfig() {
        val exception =
            RuntimeException(
                "io.debezium.DebeziumException: Error processing row in banking_safe, " +
                    "internal schema size 11, but row size 1 , restart connector with schema recovery mode.",
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
    }

    @Test
    fun testTimezoneErrorStillClassifiedAsConfig() {
        val exception =
            RuntimeException(
                "java.sql.SQLException: The server time zone value 'PDT' is unrecognized or represents more than one time zone.",
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
    }

    @Test
    fun testHikariTimeoutIsTransient() {
        val exception =
            RuntimeException(
                "java.sql.SQLTransientConnectionException: HikariPool-1 - " +
                    "Connection is not available, request timed out after 10 ms",
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
    }

    @Test
    fun testCommunicationsLinkFailureNeverConnectedIsConfigWithReachabilityGuidance() {
        // Connector/J reports a host that never answered with the "has not received any packets"
        // tail; the message carries no "Connection refused" so only the never-connected rule fires.
        val result = classifier.classify(RuntimeException(NEVER_CONNECTED_MESSAGE))
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        assertReachabilityGuidance((result as ConfigError).displayMessage)
    }

    @Test
    fun testCommunicationsLinkFailureAfterPacketsWereReceivedIsTransient() {
        // An established connection that drops mid-sync has the "successfully received" tail.
        val result = classifier.classify(RuntimeException(CONNECTION_LOST_MESSAGE))
        Assertions.assertInstanceOf(TransientError::class.java, result)
        val message: String = (result as TransientError).displayMessage
        Assertions.assertTrue(message.startsWith("MySQL EOF Exception: "), message)
        Assertions.assertTrue(
            message.contains(
                "The connection to the MySQL server was lost while reading data, will retry.",
            ),
            message,
        )
        Assertions.assertTrue(
            message.contains("https://docs.airbyte.com/integrations/sources/mysql"),
            message,
        )
    }

    @Test
    fun testCommunicationsLinkFailureRulesDoNotMatchEachOthersShape() {
        val neverConnectedRule: RegexExceptionClassifierRule =
            ruleWithPatternContaining("has not received any packets from the server")
        val connectionLostRule: RegexExceptionClassifierRule =
            ruleWithPatternContaining("successfully received from the server was")
        val neverConnected = RuntimeException(NEVER_CONNECTED_MESSAGE)
        val connectionLost = RuntimeException(CONNECTION_LOST_MESSAGE)
        Assertions.assertTrue(neverConnectedRule.matches(neverConnected))
        Assertions.assertTrue(connectionLostRule.matches(connectionLost))
        Assertions.assertFalse(
            neverConnectedRule.matches(connectionLost),
            "never-connected rule matched the connection-lost message",
        )
        Assertions.assertFalse(
            connectionLostRule.matches(neverConnected),
            "connection-lost rule matched the never-connected message",
        )
    }

    @Test
    fun testUnknownHostExceptionIsConfigWithReachabilityGuidance() {
        val exception = RuntimeException("java.net.UnknownHostException: nonexistent-host.invalid")
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        assertReachabilityGuidance((result as ConfigError).displayMessage)
    }

    @Test
    fun testConnectionRefusedIsConfigWithReachabilityGuidance() {
        val exception = RuntimeException("java.net.ConnectException: Connection refused")
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        assertReachabilityGuidance((result as ConfigError).displayMessage)
    }

    @Test
    fun testSslRequiredButNotProvidedByServerIsConfigWithTlsOptions() {
        val exception =
            RuntimeException(
                "com.mysql.cj.jdbc.exceptions.CommunicationsException: " +
                    "SSL Connection required, but not provided by server.",
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        val message: String = (result as ConfigError).displayMessage
        Assertions.assertTrue(message.contains("does not offer TLS"), message)
        Assertions.assertTrue(message.contains("enable TLS on the MySQL server"), message)
        Assertions.assertTrue(message.contains("require_secure_transport"), message)
        Assertions.assertTrue(message.contains("connect through an SSH tunnel"), message)
        Assertions.assertTrue(
            message.contains("preferred SSL mode is not accepted on Airbyte Cloud"),
            message,
        )
        Assertions.assertTrue(
            message.contains("https://docs.airbyte.com/integrations/sources/mysql"),
            message,
        )
    }

    @Test
    fun testAccessDeniedIsNotCapturedByReachabilityOrTlsRules() {
        val exception =
            RuntimeException(
                "java.sql.SQLException: Access denied for user 'airbyte'@'10.0.0.1' (using password: YES)",
            )
        Assertions.assertNull(classifier.classify(exception))
    }

    @Test
    fun testDiscoveredZeroTablesIsConfigWithGrantGuidance() {
        val result = classifier.classify(ConfigErrorException("Discovered zero tables."))
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        assertZeroTablesGuidance((result as ConfigError).displayMessage)
    }

    // The tests below go through the ExceptionHandler, i.e. the whole classifier chain, to prove
    // that the regex classifier now runs ahead of the DefaultExceptionClassifier (order: 0 in
    // application.yml) and that typed exceptions matching no rule are still mapped unchanged.

    @Test
    fun testRegexClassifierRunsBeforeDefaultAndJdbcClassifiers() {
        val names: List<String> = exceptionHandler.classifiers.map { it.javaClass.simpleName }
        Assertions.assertTrue(
            exceptionHandler.classifiers.first() is RegexExceptionClassifier,
            names.toString(),
        )
        val defaultIndex: Int =
            exceptionHandler.classifiers.indexOfFirst { it is DefaultExceptionClassifier }
        val jdbcIndex: Int =
            exceptionHandler.classifiers.indexOfFirst { it is JdbcExceptionClassifier }
        Assertions.assertTrue(defaultIndex in 1 until jdbcIndex, names.toString())
    }

    @Test
    fun testHandlerRefinesDiscoveredZeroTables() {
        val trace: AirbyteErrorTraceMessage =
            exceptionHandler.handle(ConfigErrorException("Discovered zero tables."))
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            trace.failureType,
        )
        assertZeroTablesGuidance(trace.message)
    }

    @Test
    fun testHandlerKeepsCloudUnencryptedConnectionRejectionVerbatim() {
        val trace: AirbyteErrorTraceMessage =
            exceptionHandler.handle(ConfigErrorException(CLOUD_UNENCRYPTED_REJECTION))
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            trace.failureType,
        )
        Assertions.assertEquals(CLOUD_UNENCRYPTED_REJECTION, trace.message)
    }

    @Test
    fun testHandlerKeepsEofRuleTransient() {
        val trace: AirbyteErrorTraceMessage =
            exceptionHandler.handle(
                RuntimeException(
                    "java.io.EOFException: Failed to read next byte from position 9093464",
                ),
            )
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.TRANSIENT_ERROR,
            trace.failureType,
        )
        Assertions.assertTrue(trace.message.contains("communication issue"), trace.message)
    }

    @Test
    fun testCheckFailureForDiscoveredZeroTablesCarriesGuidance() {
        val (trace, status) =
            exceptionHandler.handleCheckFailure(ConfigErrorException("Discovered zero tables."))
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            trace.failureType,
        )
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        Assertions.assertTrue(
            status.message.startsWith(
                "Could not connect with provided configuration. Error: " +
                    "No tables are visible to the configured user in the configured database.",
            ),
            status.message,
        )
        assertZeroTablesGuidance(status.message)
    }

    private fun ruleWithPatternContaining(fragment: String): RegexExceptionClassifierRule {
        val matching: List<RegexExceptionClassifierRule> =
            classifier.rules.filter { it.pattern.contains(fragment) }
        Assertions.assertEquals(
            1,
            matching.size,
            "expected exactly one rule whose pattern contains '$fragment', got " +
                matching.map { it.pattern },
        )
        return matching.first()
    }

    private fun assertReachabilityGuidance(message: String) {
        Assertions.assertTrue(
            message.contains("could not reach the database at the configured host and port"),
            message,
        )
        Assertions.assertTrue(message.contains("Check the host and port"), message)
        Assertions.assertTrue(message.contains("accepts remote connections"), message)
        Assertions.assertTrue(
            message.contains("firewall or security group allows Airbyte's IP addresses"),
            message,
        )
        Assertions.assertTrue(
            message.contains("https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist"),
            message,
        )
        Assertions.assertTrue(
            message.contains("https://docs.airbyte.com/integrations/sources/mysql"),
            message,
        )
    }

    private fun assertZeroTablesGuidance(message: String) {
        Assertions.assertTrue(
            message.contains(
                "No tables are visible to the configured user in the configured database.",
            ),
            message,
        )
        Assertions.assertTrue(
            message.contains("GRANT SELECT ON <database>.* TO '<user>'@'%'"),
            message,
        )
        Assertions.assertTrue(message.contains("check the database name"), message)
        Assertions.assertTrue(
            message.contains("check that no table filter excludes every table"),
            message,
        )
        Assertions.assertTrue(
            message.contains(
                "https://docs.airbyte.com/integrations/sources/mysql#step-1-create-a-dedicated-read-only-mysql-user",
            ),
            message,
        )
    }

    companion object {
        /**
         * Connector/J 9.1.0 message for a host that never answered (ServerPacketTimingInfoNoRecv).
         */
        const val NEVER_CONNECTED_MESSAGE: String =
            "com.mysql.cj.jdbc.exceptions.CommunicationsException: Communications link failure\n\n" +
                "The last packet sent successfully to the server was 0 milliseconds ago. " +
                "The driver has not received any packets from the server."

        /**
         * Connector/J 9.1.0 message for an established connection that dropped
         * (ServerPacketTimingInfo).
         */
        const val CONNECTION_LOST_MESSAGE: String =
            "com.mysql.cj.jdbc.exceptions.CommunicationsException: Communications link failure\n\n" +
                "The last packet successfully received from the server was 36,254 milliseconds ago. " +
                "The last packet sent successfully to the server was 36,251 milliseconds ago."

        /**
         * Copied from MySqlSourceConfigurationFactory: preferred SSL mode without a tunnel on
         * Cloud.
         */
        const val CLOUD_UNENCRYPTED_REJECTION: String =
            "Airbyte Cloud does not allow unencrypted database connections. " +
                "Either enable TLS on the MySQL server and select SSL mode required, " +
                "verify_ca or verify_identity, or configure an SSH tunnel; " +
                "the preferred SSL mode is accepted on Airbyte Cloud only together with an SSH tunnel."
    }
}
