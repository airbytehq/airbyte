/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.temporal.sync.OrchestratorConstants;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.micronaut.runtime.event.annotation.EventListener;
import io.micronaut.runtime.server.event.ServerStartupEvent;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.lang.invoke.MethodHandles;
import java.util.Map;
import java.util.function.BiFunction;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.core.LoggerContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
public class EventListeners {

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());
  private final Map<String, String> envVars;
  private final EnvConfigs configs;
  private final JobRunConfig jobRunConfig;
  private final BiFunction<String, String, Void> propertySetter;

  @Inject
  EventListeners(@Named("envVars") final Map<String, String> envVars, final EnvConfigs configs, final JobRunConfig jobRunConfig) {
    this(envVars, configs, jobRunConfig, (name, value) -> {
      System.setProperty(name, value);
      return null;
    });
  }

  /**
   * Exists only for overriding the default property setter for testing
   */
  EventListeners(@Named("envVars") final Map<String, String> envVars,
                 final EnvConfigs configs,
                 final JobRunConfig jobRunConfig,
                 final BiFunction<String, String, Void> propertySetter) {
    this.envVars = envVars;
    this.configs = configs;
    this.jobRunConfig = jobRunConfig;
    this.propertySetter = propertySetter;
  }

  /**
   * Configures the environment variables for this app.
   * <p>
   * Should this be replaced with env-vars set on the container itself?
   *
   * @param unused required so Micronaut knows when to run this event-listener, but not used
   */
  @EventListener
  void setEnvVars(final ServerStartupEvent unused) {
    log.info("settings env vars");

    OrchestratorConstants.ENV_VARS_TO_TRANSFER.stream()
        .filter(envVars::containsKey)
        .forEach(envVar -> propertySetter.apply(envVar, envVars.get(envVar)));
  }

  /**
   * Configures the logging for this app.
   *
   * @param unused required so Micronaut knows when to run this event-listener, but not used
   */
  @EventListener
  void setLogging(final ServerStartupEvent unused) {
    log.info("started logging");

    // make sure the new configuration is picked up
    final LoggerContext ctx = (LoggerContext) LogManager.getContext(false);
    ctx.reconfigure();

    LogClientSingleton.getInstance().setJobMdc(
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        TemporalUtils.getJobRoot(configs.getWorkspaceRoot(), jobRunConfig.getJobId(), jobRunConfig.getAttemptId()));
  }

}
