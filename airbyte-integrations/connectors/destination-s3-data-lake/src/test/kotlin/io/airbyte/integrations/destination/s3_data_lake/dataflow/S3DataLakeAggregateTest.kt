/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.dataflow

import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import software.amazon.awssdk.awscore.exception.AwsServiceException
import software.amazon.awssdk.services.glue.model.GlueException

internal class S3DataLakeAggregateTest {

    @Test
    fun `isThrottlingException returns true for throttling GlueException`() {
        val throttlingException =
            GlueException.builder()
                .message("Rate exceeded")
                .statusCode(400)
                .awsErrorDetails(
                    software.amazon.awssdk.awscore.exception.AwsErrorDetails.builder()
                        .errorCode("ThrottlingException")
                        .errorMessage("Rate exceeded")
                        .serviceName("Glue")
                        .sdkHttpResponse(
                            software.amazon.awssdk.http.SdkHttpResponse.builder()
                                .statusCode(400)
                                .build()
                        )
                        .build()
                )
                .build()
        assertTrue(S3DataLakeAggregate.isThrottlingException(throttlingException))
    }

    @Test
    fun `isThrottlingException returns true for wrapped throttling exception`() {
        val throttlingException =
            GlueException.builder()
                .message("Rate exceeded")
                .statusCode(400)
                .awsErrorDetails(
                    software.amazon.awssdk.awscore.exception.AwsErrorDetails.builder()
                        .errorCode("ThrottlingException")
                        .errorMessage("Rate exceeded")
                        .serviceName("Glue")
                        .sdkHttpResponse(
                            software.amazon.awssdk.http.SdkHttpResponse.builder()
                                .statusCode(400)
                                .build()
                        )
                        .build()
                )
                .build()
        val wrappedException = RuntimeException("Iceberg commit failed", throttlingException)
        assertTrue(S3DataLakeAggregate.isThrottlingException(wrappedException))
    }

    @Test
    fun `isThrottlingException returns false for non-throttling exception`() {
        val otherException =
            GlueException.builder()
                .message("Entity not found")
                .statusCode(404)
                .awsErrorDetails(
                    software.amazon.awssdk.awscore.exception.AwsErrorDetails.builder()
                        .errorCode("EntityNotFoundException")
                        .errorMessage("Entity not found")
                        .serviceName("Glue")
                        .sdkHttpResponse(
                            software.amazon.awssdk.http.SdkHttpResponse.builder()
                                .statusCode(404)
                                .build()
                        )
                        .build()
                )
                .build()
        assertFalse(S3DataLakeAggregate.isThrottlingException(otherException))
    }

    @Test
    fun `isThrottlingException returns false for non-AWS exception`() {
        assertFalse(S3DataLakeAggregate.isThrottlingException(RuntimeException("some error")))
    }
}
