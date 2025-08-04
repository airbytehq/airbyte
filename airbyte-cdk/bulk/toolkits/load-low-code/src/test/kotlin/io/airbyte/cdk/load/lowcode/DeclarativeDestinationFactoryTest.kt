/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.lowcode

import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.dlq.DisabledObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfigProvider
import io.airbyte.cdk.load.http.authentication.BasicAccessAuthenticator
import io.airbyte.cdk.util.ResourceUtils
import io.mockk.EqMatcher
import io.mockk.every
import io.mockk.mockk
import io.mockk.mockkConstructor
import io.mockk.mockkStatic
import io.mockk.unmockkStatic
import io.mockk.verify
import org.junit.jupiter.api.Test

class MockConfig(
    val apiId: String,
    val apiToken: String,
    override val objectStorageConfig: ObjectStorageConfig = DisabledObjectStorageConfig(),
) : DestinationConfiguration(), ObjectStorageConfigProvider

val VALID_API_ID: String = "api_id"
val VALID_API_TOKEN: String = "api_token"

class DeclarativeDestinationFactoryTest {

    @Test
    internal fun `test when check then ensure check gets interpolated credentials`() {
        mockManifest(
            """
            checker:
              type: HttpRequestChecker
              requester:
                type: HttpRequester
                url: https://airbyte.io/
                method: GET
                authenticator:
                  type: BasicAccessAuthenticator
                  username: "{{ config.apiId }}"
                  password: "{{ config.apiToken }}"
        """.trimIndent()
        )
        mockkConstructor(BasicAccessAuthenticator::class)
        val config = MockConfig(VALID_API_ID, VALID_API_TOKEN)
        val dlqChecker = mockk<DlqChecker>()
        every { dlqChecker.check(any()) } returns Unit

        try {
            DeclarativeDestinationFactory(config).createDestinationChecker(dlqChecker).check(config)

            verify {
                constructedWith<BasicAccessAuthenticator>(
                        EqMatcher(VALID_API_ID),
                        EqMatcher(VALID_API_TOKEN)
                    )
                    .intercept(any())
            }
        } finally {
            unmockkStatic("io.airbyte.cdk.util.ResourceUtils") // Clean up mocks
        }
    }

    private fun mockManifest(manifestContent: String) {
        // Mock ResourceUtils to return our test manifest
        mockkStatic("io.airbyte.cdk.util.ResourceUtils")
        every { ResourceUtils.readResource("manifest.yaml") } returns manifestContent
    }
}
