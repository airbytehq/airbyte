/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package config

/**
 * TODO: this currently fails with the following error:
 * @MicronautTest used on test but no bean definition for the test present. This error indicates a misconfigured build or IDE.
 * Please add the 'micronaut-inject-java' annotation processor to your test processor path
 *
 * I have verified that everything _should_ be configured as expected, but I cannot get around this issue, so punting on it for now.
 */
//@MicronautTest(propertySources = ["classpath:app-cloud.yml"])
//class FactoryTest {
//    @Inject
//    @Property(name = CONFIG_LD_KEY)
//    lateinit var apiKey: String
//
//    @Inject
//    lateinit var client: Client
//
//    @Test
//    fun `verify correct api is provided`() {
//        assert(apiKey == "example-api-key")
//    }
//
//    @Test
//    fun `verify cloud client is returned`() {
//        assert(client != null)
//    }
//
//    @MockBean(LDClient::class)
//    fun ldClient(): LDClient {
//        val client = mockk<LDClient>()
//        every { client.boolVariation(any(), any<LDUser>(), any()) } returns true
//        every { client.boolVariation(any(), any<LDContext>(), any()) } returns true
//        return client
//    }
//}