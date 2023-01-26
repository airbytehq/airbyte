/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

import com.launchdarkly.sdk.LDUser
import com.launchdarkly.sdk.server.LDClient
import io.airbyte.featureflag.ANONYMOUS
import io.airbyte.featureflag.ConfigFileClient
import io.airbyte.featureflag.EnvVar
import io.airbyte.featureflag.FeatureFlagClient
import io.airbyte.featureflag.Flag
import io.airbyte.featureflag.LaunchDarklyClient
import io.airbyte.featureflag.Temporary
import io.airbyte.featureflag.TestClient
import io.airbyte.featureflag.User
import io.airbyte.featureflag.Workspace
import io.mockk.called
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import io.mockk.verify
import org.junit.jupiter.api.Test
import java.nio.file.Path
import java.util.concurrent.TimeUnit
import kotlin.io.path.createTempFile
import kotlin.io.path.writeText
import kotlin.test.Ignore
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class ConfigFileClient {
    @Test
    fun `verify config-file functionality`() {
        val cfg = Path.of("src", "test", "resources", "feature-flags.yml")
        val client: FeatureFlagClient = ConfigFileClient(cfg)

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

    /**
     * Ignore this test for now as it is unreliable in a unit-test scenario due to the
     * unpredictable nature of knowing when the WatchService (inside the ConfigFileClient) will
     * actually see the changed file.  Currently, this test sleeps for a few seconds, which works 90%
     * of the time, however there has been instances where it has taken over 20 seconds.
     *
     * TODO: move this to a different test suite
     */
    @Test
    fun `verify no-config file returns default flag state`() {
        val client: FeatureFlagClient = ConfigFileClient(null)
        val defaultFalse = Temporary(key = "default-false")
        val defaultTrue = Temporary(key = "default-true", default = true)

        val ctx = Workspace("workspace")
        with(client) {
            assertTrue { enabled(defaultTrue, ctx) }
            assertFalse { enabled(defaultFalse, ctx) }
        }
    }

    @Test
    @Ignore
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

        val client: FeatureFlagClient = ConfigFileClient(tmpConfig)

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
        val client: FeatureFlagClient = ConfigFileClient(cfg)

        val evTrue = EnvVar(envVar = "env-true").apply { fetcher = { _ -> "true" } }
        val evFalse = EnvVar(envVar = "env-true").apply { fetcher = { _ -> "false" } }
        val evEmpty = EnvVar(envVar = "env-true").apply { fetcher = { _ -> "" } }
        val evNull = EnvVar(envVar = "env-true").apply { fetcher = { _ -> null } }

        val ctx = User("test")

        with(client) {
            assertTrue { enabled(evTrue, ctx) }
            assertFalse { enabled(evFalse, ctx) }
            assertFalse { enabled(evEmpty, ctx) }
            assertFalse { enabled(evNull, ctx) }
        }
    }
}

class LaunchDarklyClient {
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

        val client: FeatureFlagClient = LaunchDarklyClient(ldClient)
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
        val client: FeatureFlagClient = LaunchDarklyClient(ldClient)

        val evTrue = EnvVar(envVar = "env-true").apply { fetcher = { _ -> "true" } }
        val evFalse = EnvVar(envVar = "env-false").apply { fetcher = { _ -> "false" } }
        val evEmpty = EnvVar(envVar = "env-empty").apply { fetcher = { _ -> "" } }
        val evNull = EnvVar(envVar = "env-null").apply { fetcher = { _ -> null } }

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

    @Test
    fun `verify ANONYMOUS context support`() {
        val testFlag = Temporary(key = "test-true")
        val ctxAnon = Workspace(ANONYMOUS)

        val ldClient: LDClient = mockk()
        val context = slot<LDUser>()
        every {
            ldClient.boolVariation(testFlag.key, capture(context), any())
        } answers {
            true
        }

        LaunchDarklyClient(ldClient).enabled(testFlag, ctxAnon)
        assertTrue(context.captured.isAnonymous)
    }
}

class TestClient {
    @Test
    fun `verify functionality`() {
        val testTrue = Pair(Temporary(key = "test-true"), true)
        val testFalse = Pair(Temporary(key = "test-false", default = true), false)
        val testDne = Temporary(key = "test-dne")

        val ctx = User("test")
        val values: MutableMap<String, Boolean> = mutableMapOf<Flag, Boolean>(testTrue, testFalse)
            .mapKeys { it.key.key }
            .toMutableMap()

        val client: FeatureFlagClient = TestClient(values)
        with(client) {
            assertTrue { enabled(testTrue.first, ctx) }
            assertFalse { enabled(testFalse.first, ctx) }
            assertFalse { enabled(testDne, ctx) }
        }

        // modify the value, ensure the client reports the new modified value
        values[testTrue.first.key] = false
        values[testFalse.first.key] = true

        with(client) {
            assertFalse { enabled(testTrue.first, ctx) }
            assertTrue { enabled(testFalse.first, ctx) }
            assertFalse("undefined flags should always return false") { enabled(testDne, ctx) }
        }
    }

    @Test
    fun `verify env-var flag support`() {
        val evTrue = EnvVar(envVar = "env-true")
        val evFalse = EnvVar(envVar = "env-false")
        val evEmpty = EnvVar(envVar = "env-empty")

        val ctx = User("test")

        val values = mutableMapOf(
            evTrue.key to true,
            evFalse.key to false,
        )
        val client: FeatureFlagClient = TestClient(values)

        with(client) {
            assertTrue { enabled(evTrue, ctx) }
            assertFalse { enabled(evFalse, ctx) }
            assertFalse { enabled(evEmpty, ctx) }
        }

        // modify the value, ensure the client reports the new modified value
        values[evTrue.key] = false
        values[evFalse.key] = true

        with(client) {
            assertFalse { enabled(evTrue, ctx) }
            assertTrue { enabled(evFalse, ctx) }
            assertFalse("undefined flags should always return false") { enabled(evEmpty, ctx) }
        }
    }
}
