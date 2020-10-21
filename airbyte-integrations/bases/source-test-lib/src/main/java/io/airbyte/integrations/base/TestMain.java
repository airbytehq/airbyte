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
 * Parse command line arguments and inject them into the test class before running the test. Then runs the tests.
 */
public class TestMain {

  public static void main(String[] args) {
    ArgumentParser parser = ArgumentParsers.newFor(TestMain.class.getName()).build()
        .defaultHelp(true)
        .description("Run standard source tests");

    parser.addArgument("--imageName")
        .help("Name of the integration image");

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
    final String configFile = ns.getString("config");
    final String catalogFile = ns.getString("catalog");
    ExecutableTestSource.TEST_CONFIG = new TestConfig(imageName, Path.of(configFile), Path.of(catalogFile));

    // todo (cgardens) - using JUnit4 (instead of 5) here for two reasons: 1) Cannot get JUnit5 to print output nearly as nicely as 4. 2) JUnit5 was running all tests twice. Likely there are workarounds to both, but I cut my losses and went for something that worked.
    JUnitCore junit = new JUnitCore();
    junit.addListener(new TextListener(System.out));
    final Result result = junit.run(ExecutableTestSource.class);

    if (result.getFailureCount() > 0) {
      System.exit(1);
    }

//    this is how you you are supposed to do it in JUnit5
//    LauncherDiscoveryRequest request = LauncherDiscoveryRequestBuilder.request()
//        .selectors(
//            selectPackage("io.airbyte.integrations.base"),
//            selectClass(TestBasicTest.class)
//            selectClass(TestBasicTest.class, ExecutableTestSource.class)
//        )
//        .filters(includeClassNamePatterns(".*Test"))
//        .build();
//
//    TestPlan plan = LauncherFactory.create().discover(request);
//    Launcher launcher = LauncherFactory.create();
//
//
//
//    // Register a listener of your choice
//    SummaryGeneratingListener listener = new SummaryGeneratingListener();
//    launcher.registerTestExecutionListeners(listener);
//
//    launcher.execute(plan, listener);
//
//    listener.getSummary().printFailuresTo(new PrintWriter(System.out));
//    listener.getSummary().printTo(new PrintWriter(System.out));
  }
}
