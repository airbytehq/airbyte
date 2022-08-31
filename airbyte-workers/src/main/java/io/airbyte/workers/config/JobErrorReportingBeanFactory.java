/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.config;

import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.WebUrlHelper;
import io.airbyte.scheduler.persistence.job_error_reporter.JobErrorReporter;
import io.airbyte.scheduler.persistence.job_error_reporter.JobErrorReportingClient;
import io.airbyte.scheduler.persistence.job_error_reporter.LoggingJobErrorReportingClient;
import io.airbyte.scheduler.persistence.job_error_reporter.SentryExceptionHelper;
import io.airbyte.scheduler.persistence.job_error_reporter.SentryJobErrorReportingClient;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import javax.inject.Named;
import javax.inject.Singleton;

/**
 * Micronaut bean factory for job error reporting-related singletons.
 */
@Factory
@SuppressWarnings("PMD.AvoidDuplicateLiterals")
public class JobErrorReportingBeanFactory {

  @Singleton
  @Requires(property = "airbyte.worker.job.error-reporting.strategy",
            value = "SENTRY")
  @Named("jobErrorReportingClient")
  public JobErrorReportingClient sentryJobErrorReportingClient(
                                                               @Value("${airbyte.worker.job.error-reporting.sentry.dsn}") final String sentryDsn) {
    return new SentryJobErrorReportingClient(sentryDsn, new SentryExceptionHelper());
  }

  @Singleton
  @Requires(property = "airbyte.worker.job.error-reporting.strategy",
            value = "LOGGING")
  @Named("jobErrorReportingClient")
  public JobErrorReportingClient loggingJobErrorReportingClient() {
    return new LoggingJobErrorReportingClient();
  }

  @Singleton
  @Requires(property = "airbyte.worker.job.error-reporting.strategy",
            value = "")
  @Named("jobErrorReportingClient")
  public JobErrorReportingClient defaultJobErrorReportingClient() {
    return loggingJobErrorReportingClient();
  }

  @Singleton
  public JobErrorReporter jobErrorReporter(
                                           @Value("${airbyte.version}") final String airbyteVersion,
                                           final ConfigRepository configRepository,
                                           final DeploymentMode deploymentMode,
                                           @Named("jobErrorReportingClient") final JobErrorReportingClient jobErrorReportingClient,
                                           final WebUrlHelper webUrlHelper) {
    return new JobErrorReporter(
        configRepository,
        deploymentMode,
        airbyteVersion,
        NormalizationRunnerFactory.BASE_NORMALIZATION_IMAGE_NAME,
        NormalizationRunnerFactory.NORMALIZATION_VERSION,
        webUrlHelper,
        jobErrorReportingClient);
  }

}
