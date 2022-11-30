/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source;

import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;

/**
 * Parse command line arguments and inject them into the test class before running the test. Then
 * runs the tests.
 */
public class TestPythonSourceMain {

  public static void main(final String[] args) {
    final ArgumentParser parser = ArgumentParsers.newFor(TestPythonSourceMain.class.getName()).build()
        .defaultHelp(true)
        .description("Run standard source tests");

    parser.addArgument("--imageName")
        .help("Name of the integration image");

    parser.addArgument("--pythonContainerName")
        .help("Name of the python integration image");

    Namespace ns = null;
    try {
      ns = parser.parseArgs(args);
    } catch (final ArgumentParserException e) {
      parser.handleError(e);
      System.exit(1);
    }

    final String imageName = ns.getString("imageName");
    final String pythonContainerName = ns.getString("pythonContainerName");

    PythonSourceAcceptanceTest.IMAGE_NAME = imageName;
    PythonSourceAcceptanceTest.PYTHON_CONTAINER_NAME = pythonContainerName;

    TestRunner.runTestClass(PythonSourceAcceptanceTest.class);
  }

}
