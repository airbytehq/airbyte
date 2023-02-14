/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.connectorbuilder.controllers;

import io.airbyte.analytics.LoggingTrackingClient;
import io.airbyte.analytics.TrackingIdentity;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.temporal.TemporalWorkflowUtils;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.StandardConnectorBuilderReadOutput;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.connectorbuilder.ConnectorBuilderEntryPoint;
import io.airbyte.connectorbuilder.scheduler.DefaultSynchronousScheduler;
import io.airbyte.connectorbuilder.scheduler.SynchronousResponse;
import io.airbyte.connectorbuilder.temporal.TemporalClient;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.WebUrlHelper;
import io.airbyte.persistence.job.errorreporter.JobErrorReporter;
import io.airbyte.persistence.job.errorreporter.JobErrorReportingClient;
import io.airbyte.persistence.job.errorreporter.JobErrorReportingClientFactory;
import io.airbyte.persistence.job.tracker.JobTracker;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.temporal.serviceclient.WorkflowServiceStubs;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Controller("/v1/stream/read")
@Singleton
@Requires(bean = ConfigRepository.class)
@Requires(bean = JobPersistence.class)
@Slf4j
public class ReadController {

  private JobErrorReporter jobErrorReporter = null;
  private final UUID workspaceID = UUID.fromString("354ac5c4-6db5-49a6-a515-d7cfb203bc98");

  public ReadController(final ConfigRepository configRepository, final JobPersistence jobPersistence) {
    this.configRepository = configRepository;
    LoggingTrackingClient trackingClient = new LoggingTrackingClient(
        (uuid) -> new TrackingIdentity(new AirbyteVersion("1.0.0"), uuid, "email", true, false, false)); // FIXME
    jobTracker = new JobTracker(configRepository, jobPersistence, trackingClient); // fixme
    jobErrorReporter =
        new JobErrorReporter(
            configRepository,
            configs.getDeploymentMode(),
            configs.getAirbyteVersionOrWarning(),
            webUrlHelper,
            jobErrorReportingClient);
  }

  private static final Logger LOGGER = LoggerFactory.getLogger(ReadController.class);

  final Configs configs = new EnvConfigs();

  final ConfigRepository configRepository;
  final TemporalUtils temporalUtils = new TemporalUtils(
      configs.getTemporalCloudClientCert(),
      configs.getTemporalCloudClientKey(),
      configs.temporalCloudEnabled(),
      configs.getTemporalCloudHost(),
      configs.getTemporalCloudNamespace(),
      configs.getTemporalHost(),
      configs.getTemporalRetentionInDays());

  final WebUrlHelper webUrlHelper = new WebUrlHelper(configs.getWebappUrl());
  JobTracker jobTracker = null;
  final JobErrorReportingClient jobErrorReportingClient = JobErrorReportingClientFactory.getClient(configs.getJobErrorReportingStrategy(), configs);

  final WorkflowServiceStubs temporalService = temporalUtils.createTemporalService();
  final TemporalClient temporalClient = new TemporalClient(
      configs.getWorkspaceRoot(),
      TemporalWorkflowUtils.createWorkflowClient(temporalService, temporalUtils.getNamespace()),
      temporalService,
      null,
      null,
      null); // FIXME?
  final DefaultSynchronousScheduler syncSchedulerClient =
      new DefaultSynchronousScheduler(temporalClient, jobTracker, jobErrorReporter); // fixme

  @Post(produces = MediaType.APPLICATION_JSON)
  public String read(final StreamReadRequestBody body) throws IOException, InterruptedException {
    LOGGER.info("read receive: " + ConnectorBuilderEntryPoint.toJsonString(body));
    final String response = ConnectorBuilderEntryPoint.read(body);
    LOGGER.info("read send: " + response);

    final SynchronousResponse<StandardConnectorBuilderReadOutput> output =
        syncSchedulerClient.createConnectorBuilderReadJob(workspaceID, "airbyte/source-pokeapi:0.1.5");

    return output.getOutput().toString();
  }

}
