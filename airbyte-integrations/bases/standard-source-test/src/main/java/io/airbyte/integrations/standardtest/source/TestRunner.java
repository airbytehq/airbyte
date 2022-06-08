/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source;

import static org.junit.platform.engine.discovery.DiscoverySelectors.selectClass;

import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import org.junit.platform.launcher.Launcher;
import org.junit.platform.launcher.LauncherDiscoveryRequest;
import org.junit.platform.launcher.TestPlan;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;

public class TestRunner {

  public static void runTestClass(final Class<?> testClass) {
    final LauncherDiscoveryRequest request = LauncherDiscoveryRequestBuilder.request()
        .selectors(selectClass(testClass))
        .build();

    final TestPlan plan = LauncherFactory.create().discover(request);
    final Launcher launcher = LauncherFactory.create();

    // Register a listener of your choice
    final SummaryGeneratingListener listener = new SummaryGeneratingListener();

    launcher.execute(plan, listener);

    listener.getSummary().printFailuresTo(new PrintWriter(System.out, false, StandardCharsets.UTF_8));
    listener.getSummary().printTo(new PrintWriter(System.out, false, StandardCharsets.UTF_8));

    if (listener.getSummary().getTestsFailedCount() > 0) {
      System.out.println(
          "There are failing tests. See https://docs.airbyte.io/contributing-to-airbyte/building-new-connector/standard-source-tests " +
              "for more information about the standard source test suite.");
      System.exit(1);
    }
  }

}
