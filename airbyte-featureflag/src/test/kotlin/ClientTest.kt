/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

import com.launchdarkly.sdk.LDUser
import com.launchdarkly.sdk.server.LDClient
import io.airbyte.featureflag.*
import io.mockk.*
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import java.nio.file.Path
import java.util.concurrent.TimeUnit
import kotlin.io.path.createTempFile
import kotlin.io.path.writeText
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class ClientTest {
    @Nested
    inner class Platform {
        @Test
        fun `verify platform functionality`() {
            val cfg = Path.of("src", "test", "resources", "feature-flags.yml")
            val client: Client = Platform(cfg)

            val testTrue = Temporary(key = "test-true")
            val testFalse = Temporary(key = "test-false", default = true)
            val testDne = Temporary(key = "test-dne")

            val ctx = User("test")

            with(client) {
                assertTrue { enabled(testTrue, ctx) }
                assertFalse { enabled(testFalse, ctx) }
                assertFalse { enabled(testDne, ctx) }
            }
        }

        @Test
        fun `verify platform reload capabilities`() {
            val contents0 = """flags:
            |  - name: reload-test-true
            |    enabled: true
            |  - name: reload-test-false
            |    enabled: false
            |    """.trimMargin()
            val contents1 = """flags:
            |  - name: reload-test-true
            |    enabled: false
            |  - name: reload-test-false
            |    enabled: true
            |    """.trimMargin()

            // write to a temp config
            val tmpConfig = createTempFile(prefix = "reload-config", suffix = "yml").apply {
                writeText(contents0)
            }

            val client: Client = Platform(tmpConfig)

            // define the feature-flags
            val testTrue = Temporary(key = "reload-test-true")
            val testFalse = Temporary(key = "reload-test-false", default = true)
            val testDne = Temporary(key = "reload-test-dne")
            // and the context
            val ctx = User("test")

            // verify pre-updated values
            with(client) {
                assertTrue { enabled(testTrue, ctx) }
                assertFalse { enabled(testFalse, ctx) }
                assertFalse { enabled(testDne, ctx) }
            }
            // update the config and wait a few seconds (enough time for the file-watcher to pick up the change)
            tmpConfig.writeText(contents1)
            TimeUnit.SECONDS.sleep(2)

            // verify post-updated values
            with(client) {
                assertFalse { enabled(testTrue, ctx) }
                assertTrue { enabled(testFalse, ctx) }
                assertFalse("undefined flag should still be false") { enabled(testDne, ctx) }
            }
        }

        @Test
        fun `verify env-var flag support`() {
            val cfg = Path.of("src", "test", "resources", "feature-flags.yml")
            val client: Client = Platform(cfg)

            val evTrue = EnvVar(envVar = "env-true", fetcher = { _ -> "true" })
            val evFalse = EnvVar(envVar = "env-true", fetcher = { _ -> "false" })
            val evEmpty = EnvVar(envVar = "env-true", fetcher = { _ -> "" })
            val evNull = EnvVar(envVar = "env-true", fetcher = { _ -> null })

            val ctx = User("test")

            with(client) {
                assertTrue { enabled(evTrue, ctx) }
                assertFalse { enabled(evFalse, ctx) }
                assertFalse { enabled(evEmpty, ctx) }
                assertFalse { enabled(evNull, ctx) }
            }
        }
    }

    @Nested
    inner class Cloud {
        @Test
        fun `verify cloud functionality`() {
            val testTrue = Temporary(key = "test-true")
            val testFalse = Temporary(key = "test-false", default = true)
            val testDne = Temporary(key = "test-dne")

            val ctx = User("test")

            val ldClient: LDClient = mockk()
            val flag = slot<String>()
            every {
                ldClient.boolVariation(capture(flag), any<LDUser>(), any())
            } answers {
                when (flag.captured) {
                    testTrue.key -> true
                    testFalse.key, testDne.key -> false
                    else -> throw IllegalArgumentException("${flag.captured} was unexpected")
                }
            }

            val client: Client = Cloud(ldClient)
            with(client) {
                assertTrue { enabled(testTrue, ctx) }
                assertFalse { enabled(testFalse, ctx) }
                assertFalse { enabled(testDne, ctx) }
            }

            verify {
                ldClient.boolVariation(testTrue.key, any<LDUser>(), testTrue.default)
                ldClient.boolVariation(testFalse.key, any<LDUser>(), testFalse.default)
                ldClient.boolVariation(testDne.key, any<LDUser>(), testDne.default)
            }
        }

        @Test
        fun `verify env-var flag support`() {
            val ldClient: LDClient = mockk()
            val client: Client = Cloud(ldClient)

            val evTrue = EnvVar(envVar = "env-true", fetcher = { _ -> "true" })
            val evFalse = EnvVar(envVar = "env-true", fetcher = { _ -> "false" })
            val evEmpty = EnvVar(envVar = "env-true", fetcher = { _ -> "" })
            val evNull = EnvVar(envVar = "env-true", fetcher = { _ -> null })

            val ctx = User("test")

            with(client) {
                assertTrue { enabled(evTrue, ctx) }
                assertFalse { enabled(evFalse, ctx) }
                assertFalse { enabled(evEmpty, ctx) }
                assertFalse { enabled(evNull, ctx) }
            }

            // EnvVar flags should not interact with the LDClient
            verify { ldClient wasNot called }
        }
    }
}