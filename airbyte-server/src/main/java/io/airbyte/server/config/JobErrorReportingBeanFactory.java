/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.config;

import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.WebUrlHelper;
import io.airbyte.persistence.job.errorreporter.JobErrorReporter;
import io.airbyte.persistence.job.errorreporter.JobErrorReportingClient;
import io.airbyte.persistence.job.errorreporter.LoggingJobErrorReportingClient;
import io.airbyte.persistence.job.errorreporter.SentryExceptionHelper;
import io.airbyte.persistence.job.errorreporter.SentryJobErrorReportingClient;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.util.Optional;

/**
 * Micronaut bean factory for job error reporting-related singletons.
 */
@Factory
@SuppressWarnings("PMD.AvoidDuplicateLiterals")
public class JobErrorReportingBeanFactory {

  @Singleton
  @Requires(property = "airbyte.worker.job.error-reporting.strategy",
            pattern = "(?i)^sentry$")
  @Named("jobErrorReportingClient")
  public JobErrorReportingClient sentryJobErrorReportingClient(
                                                               @Value("${airbyte.worker.job.error-reporting.sentry.dsn}") final String sentryDsn) {
    return new SentryJobErrorReportingClient(sentryDsn, new SentryExceptionHelper());
  }

  @Singleton
  @Requires(property = "airbyte.worker.job.error-reporting.strategy",
            pattern = "(?i)^logging$")
  @Named("jobErrorReportingClient")
  public JobErrorReportingClient loggingJobErrorReportingClient() {
    return new LoggingJobErrorReportingClient();
  }

  @Singleton
  public JobErrorReporter jobErrorReporter(
                                           @Value("${airbyte.version}") final String airbyteVersion,
                                           final ConfigRepository configRepository,
                                           final DeploymentMode deploymentMode,
                                           @Named("jobErrorReportingClient") final Optional<JobErrorReportingClient> jobErrorReportingClient,
                                           final WebUrlHelper webUrlHelper) {
    return new JobErrorReporter(
        configRepository,
        deploymentMode,
        airbyteVersion,
        webUrlHelper,
        jobErrorReportingClient.orElseGet(() -> new LoggingJobErrorReportingClient()));
  }

}
