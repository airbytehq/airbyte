package io.airbyte.integrations.base;

import static org.junit.platform.engine.discovery.DiscoverySelectors.selectClass;

import java.io.PrintWriter;
import org.junit.platform.launcher.Launcher;
import org.junit.platform.launcher.LauncherDiscoveryRequest;
import org.junit.platform.launcher.TestPlan;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

public class TestRunner {
  public static void runTestClass(Class<?> testClass) {
    final LauncherDiscoveryRequest request = LauncherDiscoveryRequestBuilder.request()
        .selectors(selectClass(testClass))
        .build();

    final TestPlan plan = LauncherFactory.create().discover(request);
    final Launcher launcher = LauncherFactory.create();

    // Register a listener of your choice
    final SummaryGeneratingListener listener = new SummaryGeneratingListener();
    launcher.registerTestExecutionListeners(listener);

    launcher.execute(plan, listener);

    listener.getSummary().printFailuresTo(new PrintWriter(System.out));
    listener.getSummary().printTo(new PrintWriter(System.out));

    if (listener.getSummary().getTestsFailedCount() > 0) {
      System.exit(1);
    }
  }
}
