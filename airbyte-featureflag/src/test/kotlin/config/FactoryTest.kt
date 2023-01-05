/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package config

import com.launchdarkly.sdk.LDContext
import com.launchdarkly.sdk.LDUser
import com.launchdarkly.sdk.server.LDClient
import io.airbyte.featureflag.Client
import io.airbyte.featureflag.config.CONFIG_LD_KEY
import io.micronaut.context.annotation.Property
import io.micronaut.test.annotation.MockBean
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import io.mockk.every
import io.mockk.mockk
import jakarta.inject.Inject
import org.junit.jupiter.api.Test

@MicronautTest(propertySources = ["classpath:app-cloud.yml"])
class FactoryTest {
//    @MicronautTest(propertySources = ["classpath:app-platform.yml"])
//    @Test
//    fun `verify platform client is returned`() {
//
//    }

    //    @MicronautTest(propertySources = ["classpath:app-cloud.yml"])
//    @Nested
//    class CloudTest {
    @Inject
    @Property(name = CONFIG_LD_KEY)
    lateinit var apiKey: String

    @Inject
    lateinit var client: Client

    @Test
    fun `verify correct api is provided`() {
        assert(apiKey == "example-api-key")
    }

    @Test
    fun `verify cloud client is returned`() {
        assert(client != null)
    }

    @MockBean(LDClient::class)
    fun ldClient(): LDClient {
        val client = mockk<LDClient>()
        every { client.boolVariation(any(), any<LDUser>(), any()) } returns true
        every { client.boolVariation(any(), any<LDContext>(), any()) } returns true
        return client
    }
//    }
}