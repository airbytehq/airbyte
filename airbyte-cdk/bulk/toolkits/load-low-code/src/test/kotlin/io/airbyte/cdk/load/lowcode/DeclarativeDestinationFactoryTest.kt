/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.lowcode

import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.http.authentication.BasicAccessAuthenticator
import io.airbyte.cdk.load.model.checker.HttpRequestChecker
import io.airbyte.cdk.load.model.http.HttpMethod
import io.airbyte.cdk.load.model.http.HttpRequester
import io.airbyte.cdk.load.model.http.authenticator.BasicAccessAuthenticator as BasicAccessAuthenticatorModel
import io.airbyte.cdk.load.model.spec.Spec
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.AdvancedAuth
import io.mockk.EqMatcher
import io.mockk.every
import io.mockk.mockk
import io.mockk.mockkConstructor
import io.mockk.mockkStatic
import io.mockk.unmockkStatic
import io.mockk.verify
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import org.junit.jupiter.api.Test

val VALID_API_ID: String = "api_id"
val VALID_API_TOKEN: String = "api_token"

class DeclarativeDestinationFactoryTest {

    @Test
    internal fun `test when check then ensure check gets interpolated credentials`() {
        mockManifest(
            ManifestBuilder()
                .withChecker(
                    HttpRequestChecker(
                        HttpRequester(
                            url = "https://airbyte.io/",
                            method = HttpMethod.GET,
                            authenticator =
                                BasicAccessAuthenticatorModel(
                                    """{{ config["api_id"] }}""",
                                    """{{ config["api_token"] }}""",
                                ),
                        ),
                    )
                )
                .build()
        )
        mockkConstructor(BasicAccessAuthenticator::class)
        val dlqChecker = mockk<DlqChecker>()
        every { dlqChecker.check(any()) } returns Unit

        try {
            DeclarativeDestinationFactory(
                    Jsons.readTree(
                        """{"api_id": "$VALID_API_ID", "api_token": "$VALID_API_TOKEN"}"""
                    )
                )
                .createDestinationChecker(dlqChecker)
                .check()

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

    @Test
    internal fun `test when create specification then add object storage to connection specification`() {
        val advancedAuth = AdvancedAuth().withPredicateValue("a predicate value")
        mockManifest(
            ManifestBuilder()
                .withSpec(
                    Spec(
                        connectionSpecification =
                            Jsons.readTree(
                                """{"type":"object","${'$'}schema":"http://json-schema.org/draft-07/schema#","required":["account_id"],"properties":{"account_id":{"type":"string","order":0,"airbyte_secret":true}}}"""
                            ),
                        advancedAuth = advancedAuth,
                    )
                )
                .build()
        )

        val spec =
            DeclarativeDestinationFactory(Jsons.readTree("""{"account_id": "an_account_id"}"""))
                .createSpecificationFactory()
                .create()

        assertNotNull(spec.connectionSpecification.get("properties").get("account_id"))
        assertNotNull(spec.connectionSpecification.get("properties").get("object_storage_config"))
        assertEquals(advancedAuth, spec.advancedAuth)

        unmockkStatic("io.airbyte.cdk.util.ResourceUtils")
    }

    private fun mockManifest(manifestContent: String) {
        // Mock ResourceUtils to return our test manifest
        mockkStatic("io.airbyte.cdk.util.ResourceUtils")
        every { ResourceUtils.readResource("manifest.yaml") } returns manifestContent
    }
}
