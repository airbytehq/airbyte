/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import java.nio.file.Path
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class IntegrationCliParserTest {
    @Test
    fun testSpec() {
        val args = arrayOf("--spec")
        val actual = IntegrationCliParser().parse(args)
        Assertions.assertEquals(IntegrationConfig.spec(), actual)
    }

    @Test
    fun testCheck() {
        val args = arrayOf("--check", "--config", CONFIG_FILENAME)
        val actual = IntegrationCliParser().parse(args)
        Assertions.assertEquals(IntegrationConfig.check(Path.of(CONFIG_FILENAME)), actual)
    }

    @Test
    fun testDiscover() {
        val args = arrayOf("--discover", "--config", CONFIG_FILENAME)
        val actual = IntegrationCliParser().parse(args)
        Assertions.assertEquals(IntegrationConfig.discover(Path.of(CONFIG_FILENAME)), actual)
    }

    @Test
    fun testWrite() {
        val args = arrayOf("--write", "--config", CONFIG_FILENAME, "--catalog", CATALOG_FILENAME)
        val actual = IntegrationCliParser().parse(args)
        Assertions.assertEquals(
            IntegrationConfig.write(Path.of(CONFIG_FILENAME), Path.of(CATALOG_FILENAME)),
            actual
        )
    }

    @Test
    fun testReadWithoutState() {
        val args = arrayOf("--read", "--config", CONFIG_FILENAME, "--catalog", CATALOG_FILENAME)
        val actual = IntegrationCliParser().parse(args)
        Assertions.assertEquals(
            IntegrationConfig.read(Path.of(CONFIG_FILENAME), Path.of(CATALOG_FILENAME), null),
            actual
        )
    }

    @Test
    fun testReadWithState() {
        val args =
            arrayOf(
                "--read",
                "--config",
                CONFIG_FILENAME,
                "--catalog",
                CATALOG_FILENAME,
                "--state",
                STATE_FILENAME
            )
        val actual = IntegrationCliParser().parse(args)
        Assertions.assertEquals(
            IntegrationConfig.read(
                Path.of(CONFIG_FILENAME),
                Path.of(CATALOG_FILENAME),
                Path.of(STATE_FILENAME)
            ),
            actual
        )
    }

    @Test
    fun testFailsOnUnknownArg() {
        val args = arrayOf("--check", "--config", CONFIG_FILENAME, "--random", "garbage")
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            IntegrationCliParser().parse(args)
        }
    }

    companion object {
        private const val CONFIG_FILENAME = "config.json"
        private const val CATALOG_FILENAME = "catalog.json"
        private const val STATE_FILENAME = "state.json"
    }
}
