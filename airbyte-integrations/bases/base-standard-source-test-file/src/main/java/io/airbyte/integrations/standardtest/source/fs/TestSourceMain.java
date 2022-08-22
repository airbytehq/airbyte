/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source.fs;

import io.airbyte.integrations.standardtest.source.TestRunner;
import java.nio.file.Path;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Parse command line arguments and inject them into the test class before running the test. Then
 * runs the tests.
 */
public class TestSourceMain {

  private static final Logger LOGGER = LoggerFactory.getLogger(TestSourceMain.class);

  public static void main(final String[] args) {
    final ArgumentParser parser = ArgumentParsers.newFor(TestSourceMain.class.getName()).build()
        .defaultHelp(true)
        .description("Run standard source tests");

    parser.addArgument("--imageName")
        .required(true)
        .help("Name of the source connector image e.g: airbyte/source-mailchimp");

    parser.addArgument("--spec")
        .required(true)
        .help("Path to file that contains spec json");

    parser.addArgument("--config")
        .required(true)
        .help("Path to file that contains config json");

    parser.addArgument("--catalog")
        .required(true)
        .help("Path to file that contains catalog json");

    parser.addArgument("--state")
        .required(false)
        .help("Path to the file containing state");

    Namespace ns = null;
    try {
      ns = parser.parseArgs(args);
    } catch (final ArgumentParserException e) {
      parser.handleError(e);
      System.exit(1);
    }

    final String imageName = ns.getString("imageName");
    final String specFile = ns.getString("spec");
    final String configFile = ns.getString("config");
    final String catalogFile = ns.getString("catalog");
    final String stateFile = ns.getString("state");

    ExecutableTestSource.TEST_CONFIG = new ExecutableTestSource.TestConfig(
        imageName,
        Path.of(specFile),
        Path.of(configFile),
        Path.of(catalogFile),
        stateFile != null ? Path.of(stateFile) : null);

    TestRunner.runTestClass(ExecutableTestSource.class);
  }

}
