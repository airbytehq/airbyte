/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron;

import io.airbyte.commons.temporal.TemporalInitializationUtils;
import io.airbyte.featureflag.FeatureFlagClient;
import io.airbyte.featureflag.PerfBackgroundJsonValidation;
import io.airbyte.featureflag.Workspace;
import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.discovery.event.ServiceReadyEvent;
import jakarta.inject.Inject;
import java.lang.invoke.MethodHandles;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ApplicationInitializer implements ApplicationEventListener<ServiceReadyEvent> {

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());
  @Inject
  private TemporalInitializationUtils temporalInitializationUtils;

  @Inject
  private FeatureFlagClient featureFlagClient;

  @Override

  public void onApplicationEvent(final ServiceReadyEvent event) {
    final var enabled = featureFlagClient.enabled(PerfBackgroundJsonValidation.INSTANCE, new Workspace("anything"));
    log.info("!!! perf background flag is set to {} !!!", enabled);
    temporalInitializationUtils.waitForTemporalNamespace();
  }

}
