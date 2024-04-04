/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.operation.executor

import com.amazonaws.services.s3.AmazonS3
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.integrations.destination.s3.operation.executor.CloudCheckOperationExecutor.Companion.UNSECURED_ENDPOINT_FAILURE_MESSAGE
import io.airbyte.integrations.destination.s3.service.S3CheckService
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
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
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST, "cloud", "destination"])
@Property(name = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION, value = "check")
class CloudCheckOperationExecutorTest {
    @Inject
    lateinit var cloudCheckOperationExecutor: CloudCheckOperationExecutor

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
    @Property(name = "${ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX}.s3-endpoint", value = "https://secured")
    internal fun `test that when the configured endpoint is secured, the executor invokes the check service`() {
        every { checkService.check() } returns Result.success(mockk<AirbyteMessage>())

        val result = cloudCheckOperationExecutor.execute()

        assertTrue(result.isSuccess)
        verify(exactly = 1) { checkService.check() }
    }

    @Test
    @Property(name = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION, value = "check")
    @Property(name = "${ConnectorConfigurationPropertySource.CONNECTOR_CONFIG_PREFIX}.s3-endpoint", value = "http://unsecured")
    internal fun `test that if the configured endpoint is not secure, a successful response with a failed status is returned`() {
        val result = cloudCheckOperationExecutor.execute()

        assertTrue(result.isSuccess)
        assertEquals(AirbyteConnectionStatus.Status.FAILED, result.getOrNull()?.connectionStatus?.status)
        assertEquals(UNSECURED_ENDPOINT_FAILURE_MESSAGE, result.getOrNull()?.connectionStatus?.message)

        verify(exactly = 0) { checkService.check() }
    }
}
