/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.featureflag.Client
import io.airbyte.featureflag.Platform
import io.airbyte.featureflag.Temporary
import io.airbyte.featureflag.User
import org.junit.jupiter.api.Test
import java.nio.file.Path
import java.util.concurrent.TimeUnit
import kotlin.io.path.createTempFile
import kotlin.io.path.writeText

class ClientTest {
    @Test
    fun `verify platform functionality`() {
        val cfg = Path.of("src", "test", "resources", "feature-flags.yml")
        val client: Client = Platform(cfg)

        val testTrue = Temporary(key = "test-true")
        val testFalse = Temporary(key = "test-false", default = true)
        val testDne = Temporary(key = "test-dne")

        val ctx = User("test")

        with(client) {
            assert(enabled(testTrue, ctx))
            assert(!enabled(testFalse, ctx))
            assert(!enabled(testDne, ctx))
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
        val contents1 = """ flags:
            |  - name: reload-test-true
            |    enabled: false
            |  - name: reload-test-false
            |    enabled: true
            |    """.trimMargin()

        // write to a temp config
        val tmpConfig = createTempFile(prefix = "reload-config", suffix = "yml").also {
            it.writeText(contents0)
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
            assert(enabled(testTrue, ctx))
            assert(!enabled(testFalse, ctx))
            assert(!enabled(testDne, ctx))
        }
        // update the config and wait for 5 seconds (enough time for the file-watcher to pick up the change)
        tmpConfig.writeText(contents1).also { TimeUnit.SECONDS.sleep(5) }

        // verify post-updated values
        with(client) {
            assert(!enabled(testTrue, ctx))
            assert(enabled(testFalse, ctx))
            assert(!enabled(testDne, ctx))
        }
    }
}