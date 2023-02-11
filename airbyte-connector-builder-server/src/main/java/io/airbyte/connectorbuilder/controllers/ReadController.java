/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.connectorbuilder.controllers;

import io.airbyte.commons.temporal.TemporalClient;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.temporal.TemporalWorkflowUtils;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.StandardConnectorBuilderReadOutput;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.connectorbuilder.ConnectorBuilderEntryPoint;
import io.airbyte.connectorbuilder.scheduler.DefaultSynchronousScheduler;
import io.airbyte.connectorbuilder.scheduler.SynchronousResponse;
import io.airbyte.persistence.job.WebUrlHelper;
import io.airbyte.persistence.job.errorreporter.JobErrorReporter;
import io.airbyte.persistence.job.errorreporter.JobErrorReportingClient;
import io.airbyte.persistence.job.errorreporter.JobErrorReportingClientFactory;
import io.airbyte.persistence.job.tracker.JobTracker;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Controller("/v1/stream/read")
public class ReadController {

  private static final Logger LOGGER = LoggerFactory.getLogger(ReadController.class);

  final Configs configs = new EnvConfigs();
  final ConfigRepository configRepository = new ConfigRepository(null); //fixme
  final TemporalUtils temporalUtils = new TemporalUtils(
      configs.getTemporalCloudClientCert(),
      configs.getTemporalCloudClientKey(),
      configs.temporalCloudEnabled(),
      configs.getTemporalCloudHost(),
      configs.getTemporalCloudNamespace(),
      configs.getTemporalHost(),
      configs.getTemporalRetentionInDays());
  final WebUrlHelper webUrlHelper = new WebUrlHelper(configs.getWebappUrl());
  final JobTracker jobTracker = new JobTracker(configRepository, null, null); //fixme
  final JobErrorReportingClient jobErrorReportingClient = JobErrorReportingClientFactory.getClient(configs.getJobErrorReportingStrategy(), configs);

  final JobErrorReporter jobErrorReporter =
      new JobErrorReporter(
          configRepository,
          configs.getDeploymentMode(),
          configs.getAirbyteVersionOrWarning(),
          webUrlHelper,
          jobErrorReportingClient);
  final WorkflowServiceStubs temporalService = temporalUtils.createTemporalService();
  final TemporalClient temporalClient = new TemporalClient(
      configs.getWorkspaceRoot(),
      TemporalWorkflowUtils.createWorkflowClient(temporalService, temporalUtils.getNamespace()),
      temporalService,
      null,
      null,
      null); //FIXME?
  final DefaultSynchronousScheduler syncSchedulerClient =
      new DefaultSynchronousScheduler(temporalClient, jobTracker, jobErrorReporter); //fixme

  @Post(produces = MediaType.APPLICATION_JSON)
  public String manifest(final StreamReadRequestBody body) throws IOException, InterruptedException {
    LOGGER.info("read receive: " + ConnectorBuilderEntryPoint.toJsonString(body));
    final String response = ConnectorBuilderEntryPoint.read(body);
    LOGGER.info("read send: " + response);

    final SynchronousResponse<StandardConnectorBuilderReadOutput> output =
        syncSchedulerClient.createConnectorBuilderReadJob("airbyte-cdk:dev");


    return output.toString();
  }

}
