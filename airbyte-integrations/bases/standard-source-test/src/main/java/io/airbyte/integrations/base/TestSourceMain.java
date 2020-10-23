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
import org.junit.internal.TextListener;
import org.junit.runner.JUnitCore;
import org.junit.runner.Result;

/**
 * Parse command line arguments and inject them into the test class before running the test. Then
 * runs the tests.
 */
public class TestSourceMain {

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

    // todo (cgardens) - using JUnit4 (instead of 5) here for two reasons: 1) Cannot get JUnit5 to print
    // output nearly as nicely as 4. 2) JUnit5 was running all tests twice. Likely there are workarounds
    // to both, but I cut my losses and went for something that worked.
    JUnitCore junit = new JUnitCore();
    junit.addListener(new TextListener(System.out));
    final Result result = junit.run(ExecutableTestSource.class);

    if (result.getFailureCount() > 0) {
      System.exit(1);
    }

    // this is how you you are supposed to do it in JUnit5
    // LauncherDiscoveryRequest request = LauncherDiscoveryRequestBuilder.request()
    // .selectors(
    // selectPackage("io.airbyte.integrations.base"),
    // selectClass(TestBasicTest.class)
    // selectClass(TestBasicTest.class, ExecutableTestSource.class)
    // )
    // .filters(includeClassNamePatterns(".*Test"))
    // .build();
    //
    // TestPlan plan = LauncherFactory.create().discover(request);
    // Launcher launcher = LauncherFactory.create();
    //
    //
    //
    // // Register a listener of your choice
    // SummaryGeneratingListener listener = new SummaryGeneratingListener();
    // launcher.registerTestExecutionListeners(listener);
    //
    // launcher.execute(plan, listener);
    //
    // listener.getSummary().printFailuresTo(new PrintWriter(System.out));
    // listener.getSummary().printTo(new PrintWriter(System.out));
  }

}
