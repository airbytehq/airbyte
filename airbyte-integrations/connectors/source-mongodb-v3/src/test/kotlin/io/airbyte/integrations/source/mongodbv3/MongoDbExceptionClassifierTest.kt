/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.RegexExceptionClassifier
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/** Verifies the `application.yml` exception-classifier rules map driver errors to user messages. */
@MicronautTest
class MongoDbExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Test
    fun testBsonObjectTooLargeIsAnActionableConfigError() {
        val exception =
            RuntimeException(
                "com.mongodb.MongoCommandException: Command failed with error 10334 (BSONObjectTooLarge): " +
                    "'BSONObj size: 16810000 (0x1008B90) is invalid. Size must be between 0 and " +
                    "16793600(16MB)' on server mongo:27017.",
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        val message = (result as ConfigError).displayMessage
        Assertions.assertTrue(message.contains("exceeds the 16MB BSON size limit"), message)
        Assertions.assertTrue(message.contains("'Full Refresh' sync mode"), message)
    }

    @Test
    fun testBsonObjectTooLargeMatchesOnCauseChain() {
        val exception =
            RuntimeException(
                "wrapper",
                RuntimeException("Command failed with error 10334 (BSONObjectTooLarge): too big"),
            )
        Assertions.assertInstanceOf(ConfigError::class.java, classifier.classify(exception))
    }

    @Test
    fun testAuthenticationFailureKeepsLegacyMessage() {
        val exception =
            RuntimeException(
                "com.mongodb.MongoSecurityException: Exception authenticating " +
                    "MongoCredential{mechanism=SCRAM-SHA-256, userName='root', source='admin'}",
            )
        val result = classifier.classify(exception)
        Assertions.assertEquals(
            "Authentication failed.  Please check the source's configured credentials.",
            (result as ConfigError).displayMessage,
        )
    }

    @Test
    fun testUnrelatedErrorIsNotClassified() {
        Assertions.assertNull(classifier.classify(RuntimeException("something else entirely")))
    }
}
