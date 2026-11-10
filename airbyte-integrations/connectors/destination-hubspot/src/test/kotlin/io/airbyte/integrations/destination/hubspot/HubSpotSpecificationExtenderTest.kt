/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.hubspot

import io.airbyte.cdk.load.spec.DestinationSpecificationExtender
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.mockk.every
import io.mockk.mockk
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test

class HubSpotSpecificationExtenderTest {
    @Test
    fun `OAuth specification provides a complete S256 PKCE flow`() {
        val decorated = mockk<DestinationSpecificationExtender>()
        val specification = ConnectorSpecification()
        every { decorated.invoke(specification) } returns specification

        val oauth =
            HubSpotSpecificationExtender(decorated)
                .invoke(specification)
                .advancedAuth
                .oauthConfigSpecification
                .oauthConnectorInputSpecification

        val consentUrl = oauth["consent_url"].asText()
        assertTrue(consentUrl.contains("code_challenge={{ state_value | codechallengeS256 }}"))
        assertTrue(consentUrl.contains("code_challenge_method=S256"))
        assertEquals("{{ state_value }}", oauth["access_token_params"]["code_verifier"]?.asText())
        val state = oauth["state"]
        assertTrue(state != null && state["min"].asInt() >= 43)
        assertTrue(state != null && state["max"].asInt() <= 128)
        assertTrue(state["min"].asInt() <= state["max"].asInt())
    }
}
