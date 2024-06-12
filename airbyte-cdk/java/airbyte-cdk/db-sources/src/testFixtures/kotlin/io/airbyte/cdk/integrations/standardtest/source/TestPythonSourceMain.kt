/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.source

import net.sourceforge.argparse4j.ArgumentParsers
import net.sourceforge.argparse4j.inf.ArgumentParserException
import net.sourceforge.argparse4j.inf.Namespace

/**
 * Parse command line arguments and inject them into the test class before running the test. Then
 * runs the tests.
 */
object TestPythonSourceMain {
    @JvmStatic
    fun main(args: Array<String>) {
        val parser =
            ArgumentParsers.newFor(TestPythonSourceMain::class.java.name)
                .build()
                .defaultHelp(true)
                .description("Run standard source tests")

        parser.addArgument("--imageName").help("Name of the integration image")

        parser.addArgument("--pythonContainerName").help("Name of the python integration image")

        var ns: Namespace? = null
        try {
            ns = parser.parseArgs(args)
        } catch (e: ArgumentParserException) {
            parser.handleError(e)
            System.exit(1)
        }

        val imageName = ns!!.getString("imageName")
        val pythonContainerName = ns.getString("pythonContainerName")

        PythonSourceAcceptanceTest.Companion.IMAGE_NAME = imageName
        PythonSourceAcceptanceTest.Companion.PYTHON_CONTAINER_NAME = pythonContainerName

        TestRunner.runTestClass(PythonSourceAcceptanceTest::class.java)
    }
}
