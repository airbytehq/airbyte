/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.cli

import org.apache.commons.cli.DefaultParser
import org.apache.commons.cli.Option
import org.apache.commons.cli.Options
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class ClisTest {
    @Test
    fun testParse() {
        val optionA = Option.builder("a").required(true).hasArg(true).build()
        val optionB = Option.builder("b").required(true).hasArg(true).build()
        val options = Options().addOption(optionA).addOption(optionB)
        val args = arrayOf("-a", ALPHA, "-b", BETA)
        val parsed = Clis.parse(args, options, DefaultParser())
        Assertions.assertEquals(ALPHA, parsed.options[0].value)
        Assertions.assertEquals(BETA, parsed.options[1].value)
    }

    @Test
    fun testParseNonConforming() {
        val optionA = Option.builder("a").required(true).hasArg(true).build()
        val optionB = Option.builder("b").required(true).hasArg(true).build()
        val options = Options().addOption(optionA).addOption(optionB)
        val args = arrayOf("-a", ALPHA, "-b", BETA, "-c", "charlie")
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            Clis.parse(args, options, DefaultParser())
        }
    }

    @Test
    fun testParseNonConformingWithSyntax() {
        val optionA = Option.builder("a").required(true).hasArg(true).build()
        val optionB = Option.builder("b").required(true).hasArg(true).build()
        val options = Options().addOption(optionA).addOption(optionB)
        val args = arrayOf("-a", ALPHA, "-b", BETA, "-c", "charlie")
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            Clis.parse(args, options, DefaultParser(), "search")
        }
    }

    @Test
    fun testRelaxedParser() {
        val optionA = Option.builder("a").required(true).hasArg(true).build()
        val optionB = Option.builder("b").required(true).hasArg(true).build()
        val options = Options().addOption(optionA).addOption(optionB)
        val args = arrayOf("-a", ALPHA, "-b", BETA, "-c", "charlie")
        val parsed = Clis.parse(args, options, Clis.getRelaxedParser())
        Assertions.assertEquals(ALPHA, parsed.options[0].value)
        Assertions.assertEquals(BETA, parsed.options[1].value)
    }

    companion object {
        private const val ALPHA = "alpha"
        private const val BETA = "beta"
    }
}
