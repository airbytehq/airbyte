/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.source.fs

import io.airbyte.cdk.integrations.standardtest.source.TestRunner
import java.nio.file.Path
import net.sourceforge.argparse4j.ArgumentParsers
import net.sourceforge.argparse4j.inf.ArgumentParserException
import net.sourceforge.argparse4j.inf.Namespace

/**
 * Parse command line arguments and inject them into the test class before running the test. Then
 * runs the tests.
 */
object TestSourceMain {

    @JvmStatic
    fun main(args: Array<String>) {
        val parser =
            ArgumentParsers.newFor(TestSourceMain::class.java.name)
                .build()
                .defaultHelp(true)
                .description("Run standard source tests")

        parser
            .addArgument("--imageName")
            .required(true)
            .help("Name of the source connector image e.g: airbyte/source-mailchimp")

        parser.addArgument("--spec").required(true).help("Path to file that contains spec json")

        parser.addArgument("--config").required(true).help("Path to file that contains config json")

        parser
            .addArgument("--catalog")
            .required(true)
            .help("Path to file that contains catalog json")

        parser.addArgument("--state").required(false).help("Path to the file containing state")

        var ns: Namespace? = null
        try {
            ns = parser.parseArgs(args)
        } catch (e: ArgumentParserException) {
            parser.handleError(e)
            System.exit(1)
        }

        val imageName = ns!!.getString("imageName")
        val specFile = ns.getString("spec")
        val configFile = ns.getString("config")
        val catalogFile = ns.getString("catalog")
        val stateFile = ns.getString("state")

        ExecutableTestSource.Companion.TEST_CONFIG =
            ExecutableTestSource.TestConfig(
                imageName,
                Path.of(specFile),
                Path.of(configFile),
                Path.of(catalogFile),
                if (stateFile != null) Path.of(stateFile) else null
            )

        TestRunner.runTestClass(ExecutableTestSource::class.java)
    }
}
