/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import java.nio.file.Path
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class IntegrationConfigTest {
    @Test
    fun testSpec() {
        val config = IntegrationConfig.spec()
        Assertions.assertEquals(Command.SPEC, config.command)
        Assertions.assertThrows(IllegalStateException::class.java) { config.getConfigPath() }
        Assertions.assertThrows(IllegalStateException::class.java) { config.getCatalogPath() }
        Assertions.assertThrows(IllegalStateException::class.java) { config.getStatePath() }
    }

    @Test
    fun testCheck() {
        Assertions.assertThrows(NullPointerException::class.java) { IntegrationConfig.check(null) }

        val config = IntegrationConfig.check(CONFIG_PATH)
        Assertions.assertEquals(Command.CHECK, config.command)
        Assertions.assertEquals(CONFIG_PATH, config.getConfigPath())
        Assertions.assertThrows(IllegalStateException::class.java) { config.getCatalogPath() }
        Assertions.assertThrows(IllegalStateException::class.java) { config.getStatePath() }
    }

    @Test
    fun testDiscover() {
        Assertions.assertThrows(NullPointerException::class.java) {
            IntegrationConfig.discover(null)
        }

        val config = IntegrationConfig.discover(CONFIG_PATH)
        Assertions.assertEquals(Command.DISCOVER, config.command)
        Assertions.assertEquals(CONFIG_PATH, config.getConfigPath())
        Assertions.assertThrows(IllegalStateException::class.java) { config.getCatalogPath() }
        Assertions.assertThrows(IllegalStateException::class.java) { config.getStatePath() }
    }

    @Test
    fun testWrite() {
        Assertions.assertThrows(NullPointerException::class.java) {
            IntegrationConfig.write(null, CATALOG_PATH)
        }
        Assertions.assertThrows(NullPointerException::class.java) {
            IntegrationConfig.write(CONFIG_PATH, null)
        }

        val config = IntegrationConfig.write(CONFIG_PATH, CATALOG_PATH)
        Assertions.assertEquals(Command.WRITE, config.command)
        Assertions.assertEquals(CONFIG_PATH, config.getConfigPath())
        Assertions.assertEquals(CATALOG_PATH, config.getCatalogPath())
        Assertions.assertThrows(IllegalStateException::class.java) { config.getStatePath() }
    }

    @Test
    fun testReadWithState() {
        Assertions.assertThrows(NullPointerException::class.java) {
            IntegrationConfig.read(null, CATALOG_PATH, STATE_PATH)
        }
        Assertions.assertThrows(NullPointerException::class.java) {
            IntegrationConfig.read(CONFIG_PATH, null, STATE_PATH)
        }

        val config = IntegrationConfig.read(CONFIG_PATH, CATALOG_PATH, STATE_PATH)
        Assertions.assertEquals(Command.READ, config.command)
        Assertions.assertEquals(CONFIG_PATH, config.getConfigPath())
        Assertions.assertEquals(CATALOG_PATH, config.getCatalogPath())
        Assertions.assertEquals(Optional.of(STATE_PATH), config.getStatePath())
    }

    @Test
    fun testReadWithoutState() {
        Assertions.assertThrows(NullPointerException::class.java) {
            IntegrationConfig.read(null, CATALOG_PATH, null)
        }
        Assertions.assertThrows(NullPointerException::class.java) {
            IntegrationConfig.read(CONFIG_PATH, null, null)
        }

        val config = IntegrationConfig.read(CONFIG_PATH, CATALOG_PATH, null)
        Assertions.assertEquals(Command.READ, config.command)
        Assertions.assertEquals(CONFIG_PATH, config.getConfigPath())
        Assertions.assertEquals(CATALOG_PATH, config.getCatalogPath())
        Assertions.assertEquals(Optional.empty<Any>(), config.getStatePath())
    }

    companion object {
        private val CONFIG_PATH: Path = Path.of("config.json")
        private val CATALOG_PATH: Path = Path.of("catalog.json")
        private val STATE_PATH: Path = Path.of("state.json")
    }
}
