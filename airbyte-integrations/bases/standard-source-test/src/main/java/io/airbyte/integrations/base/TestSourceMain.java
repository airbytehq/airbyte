/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.base;

import io.airbyte.integrations.base.ExecutableTestSource.TestConfig;
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

  public static void main(String[] args) {
    ArgumentParser parser = ArgumentParsers.newFor(TestSourceMain.class.getName()).build()
        .defaultHelp(true)
        .description("Run standard source tests");

    parser.addArgument("--imageName")
        .help("Name of the integration image");

    parser.addArgument("--spec")
        .help("Path to file that contains spec json");

    parser.addArgument("--config")
        .help("Path to file that contains config json");

    parser.addArgument("--catalog")
        .help("Path to file that contains catalog json");

    Namespace ns = null;
    try {
      ns = parser.parseArgs(args);
    } catch (ArgumentParserException e) {
      parser.handleError(e);
      System.exit(1);
    }

    final String imageName = ns.getString("imageName");
    final String specFile = ns.getString("spec");
    final String configFile = ns.getString("config");
    final String catalogFile = ns.getString("catalog");
    ExecutableTestSource.TEST_CONFIG = new TestConfig(imageName, Path.of(specFile), Path.of(configFile), Path.of(catalogFile));

    TestRunner.runTestClass(ExecutableTestSource.class);
  }

}
