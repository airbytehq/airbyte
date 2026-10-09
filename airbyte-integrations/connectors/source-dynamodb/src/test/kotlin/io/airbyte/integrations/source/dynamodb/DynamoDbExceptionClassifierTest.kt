/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.RegexExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import software.amazon.awssdk.awscore.exception.AwsErrorDetails
import software.amazon.awssdk.services.dynamodb.model.ProvisionedThroughputExceededException
import software.amazon.awssdk.services.dynamodb.model.ThrottlingException

@MicronautTest
class DynamoDbExceptionClassifierTest {

    @Inject lateinit var classifier: RegexExceptionClassifier

    @Test
    fun testOnDemandMaxThroughputExceededIsAConfigErrorWithoutRequestId() {
        // The message of the exception in https://github.com/airbytehq/oncall/issues/13650.
        val exception: ThrottlingException =
            throttling(
                ThrottlingException.builder(),
                "ThrottlingException",
                "Throughput exceeds the maximum OnDemandThroughput configured on table or index " +
                    "(Service: DynamoDb, Status Code: 400, Request ID: " +
                    "Q9N0V29QBKQITSM48HCF5KMCERVV4KQNSO5AEMVJF66Q9ASUAAJG) (SDK Attempt Count: 9)",
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(ConfigError::class.java, result)
        val message: String = (result as ConfigError).displayMessage
        Assertions.assertTrue(
            message.contains("maximum on-demand read throughput"),
            "Expected the message to name the on-demand maximum, got: $message",
        )
        Assertions.assertTrue(message.contains("Max Concurrent Queries to Database"), message)
        Assertions.assertFalse(message.contains("Request ID"), message)
    }

    @Test
    fun testProvisionedThroughputExceededIsTransientWithoutRequestId() {
        val exception: ProvisionedThroughputExceededException =
            throttling(
                ProvisionedThroughputExceededException.builder(),
                "ProvisionedThroughputExceededException",
                "The level of configured provisioned throughput for the table was exceeded. " +
                    "Consider increasing your provisioning level with the UpdateTable API. " +
                    "(Service: DynamoDb, Status Code: 400, Request ID: ABC) (SDK Attempt Count: 9)",
            )
        val result = classifier.classify(exception)
        Assertions.assertInstanceOf(TransientError::class.java, result)
        val message: String = (result as TransientError).displayMessage
        Assertions.assertTrue(message.contains("read capacity"), message)
        Assertions.assertFalse(message.contains("Request ID"), message)
    }

    @Test
    fun testGenericThrottlingIsTransient() {
        val exception: ThrottlingException =
            throttling(
                ThrottlingException.builder(),
                "ThrottlingException",
                "Rate of requests exceeds the allowed throughput. (Service: DynamoDb, " +
                    "Status Code: 400, Request ID: ABC)",
            )
        Assertions.assertInstanceOf(TransientError::class.java, classifier.classify(exception))
    }

    companion object {
        /** Builds a DynamoDB service exception the way the AWS SDK does for an error response. */
        @Suppress("UNCHECKED_CAST")
        fun <
            B : software.amazon.awssdk.services.dynamodb.model.DynamoDbException.Builder, E
        > throttling(
            builder: B,
            errorCode: String,
            message: String,
        ): E =
            builder
                .message(message)
                .statusCode(400)
                .awsErrorDetails(
                    AwsErrorDetails.builder()
                        .errorCode(errorCode)
                        .errorMessage(message.substringBefore(" (Service:"))
                        .serviceName("DynamoDb")
                        .build()
                )
                .build() as E
    }
}
