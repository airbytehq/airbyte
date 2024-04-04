/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.operation.executor

import com.amazonaws.services.s3.AmazonS3
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.integrations.destination.s3.service.S3CheckService
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.annotation.MockBean
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import jakarta.inject.Inject
import jakarta.inject.Singleton
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow

@MicronautTest(environments = [Environment.TEST, "destination"])
@Property(name = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION, value = "check")
class S3CheckOperationExecutorTest {
    @Inject
    lateinit var s3CheckOperationExecutor: S3CheckOperationExecutor

    private val amazonS3Client: AmazonS3 = mockk()
    private val checkService: S3CheckService = mockk()

    @MockBean
    fun amazonS3Client(): AmazonS3 {
        return amazonS3Client
    }

    @Singleton
    @Primary
    fun s3CheckService(): S3CheckService {
        return checkService
    }

    @Test
    internal fun `test that when the operation executor is invoked, the check service is called`() {
        every { checkService.check() } returns Result.success(mockk<AirbyteMessage>())

        assertDoesNotThrow {
            s3CheckOperationExecutor.execute()
        }

        verify(exactly = 1) { checkService.check() }
    }
}
