/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.server.handlers.*;
import io.airbyte.commons.server.scheduler.SynchronousSchedulerClient;
import io.airbyte.commons.temporal.TemporalClient;
import io.airbyte.db.Database;
import io.micronaut.context.annotation.Replaces;
import io.micronaut.context.annotation.Requires;
import io.micronaut.core.util.StringUtils;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.client.HttpClient;
import io.micronaut.http.client.annotation.Client;
import io.micronaut.http.client.exceptions.HttpClientResponseException;
import io.micronaut.runtime.server.EmbeddedServer;
import io.micronaut.test.annotation.MockBean;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import javax.sql.DataSource;
import org.assertj.core.api.Assertions;
import org.assertj.core.api.Condition;
import org.assertj.core.api.InstanceOfAssertFactory;
import org.jooq.DSLContext;
import org.mockito.Mockito;

/**
 * This is the base class for the test of the controllers. This allows to test that:
 * <ul>
 * <li>The path defined at the moment of writing the test exists,</li>
 * <li>The return code is the expected one. It could have help to catch that during the migration to
 * micronaut, some endpoint return value switch from a 204 NO_CONTENT return code to a 200 OK which
 * was a regression,</li>
 * <li>It allow to test that the exception thrown by the handler are properly catch by the exception
 * handlers and then return an expected HTTP return code,</li>
 * <li>It could help with testing the authorization by injecting a user and workspace in the header
 * and check that the authorization is properly applied.</li>
 * </ul>
 */
@MicronautTest
@Requires(property = "mockito.test.enabled",
          defaultValue = StringUtils.TRUE,
          value = StringUtils.TRUE)
@SuppressWarnings("PMD.AbstractClassWithoutAbstractMethod")
abstract class BaseControllerTest {

  AttemptHandler attemptHandler = Mockito.mock(AttemptHandler.class);

  @MockBean(AttemptHandler.class)
  @Replaces(AttemptHandler.class)
  AttemptHandler mAttemptHandler() {
    return attemptHandler;
  }

  ConnectionsHandler connectionsHandler = Mockito.mock(ConnectionsHandler.class);

  @MockBean(ConnectionsHandler.class)
  @Replaces(ConnectionsHandler.class)
  ConnectionsHandler mConnectionsHandler() {
    return connectionsHandler;
  }

  DestinationHandler destinationHandler = Mockito.mock(DestinationHandler.class);

  @MockBean(DestinationHandler.class)
  @Replaces(DestinationHandler.class)
  DestinationHandler mDestinationHandler() {
    return destinationHandler;
  }

  DestinationDefinitionsHandler destinationDefinitionsHandler = Mockito.mock(DestinationDefinitionsHandler.class);

  @MockBean(DestinationDefinitionsHandler.class)
  @Replaces(DestinationDefinitionsHandler.class)
  DestinationDefinitionsHandler mDestinationDefinitionsHandler() {
    return destinationDefinitionsHandler;
  }

  HealthCheckHandler healthCheckHandler = Mockito.mock(HealthCheckHandler.class);

  @MockBean(HealthCheckHandler.class)
  @Replaces(HealthCheckHandler.class)
  HealthCheckHandler mHealthCheckHandler() {
    return healthCheckHandler;
  }

  JobHistoryHandler jobHistoryHandler = Mockito.mock(JobHistoryHandler.class);

  @MockBean(JobHistoryHandler.class)
  @Replaces(JobHistoryHandler.class)
  JobHistoryHandler mJobHistoryHandler() {
    return jobHistoryHandler;
  }

  LogsHandler logsHandler = Mockito.mock(LogsHandler.class);

  @MockBean(LogsHandler.class)
  @Replaces(LogsHandler.class)
  LogsHandler mLogsHandler() {
    return logsHandler;
  }

  OAuthHandler oAuthHandler = Mockito.mock(OAuthHandler.class);

  @MockBean(OAuthHandler.class)
  @Replaces(OAuthHandler.class)
  OAuthHandler mOAuthHandler() {
    return oAuthHandler;
  }

  OpenApiConfigHandler openApiConfigHandler = Mockito.mock(OpenApiConfigHandler.class);

  @MockBean(OpenApiConfigHandler.class)
  @Replaces(OpenApiConfigHandler.class)
  OpenApiConfigHandler mOpenApiConfigHandler() {
    return openApiConfigHandler;
  }

  OperationsHandler operationsHandler = Mockito.mock(OperationsHandler.class);

  @MockBean(OperationsHandler.class)
  @Replaces(OperationsHandler.class)
  OperationsHandler mOperationsHandler() {
    return operationsHandler;
  }

  SchedulerHandler schedulerHandler = Mockito.mock(SchedulerHandler.class);

  @MockBean(SchedulerHandler.class)
  @Replaces(SchedulerHandler.class)
  SchedulerHandler mSchedulerHandler() {
    return schedulerHandler;
  }

  SourceDefinitionsHandler sourceDefinitionsHandler = Mockito.mock(SourceDefinitionsHandler.class);

  @MockBean(SourceDefinitionsHandler.class)
  @Replaces(SourceDefinitionsHandler.class)
  SourceDefinitionsHandler mSourceDefinitionsHandler() {
    return sourceDefinitionsHandler;
  }

  SourceHandler sourceHandler = Mockito.mock(SourceHandler.class);

  @MockBean(SourceHandler.class)
  @Replaces(SourceHandler.class)
  SourceHandler mSourceHandler() {
    return sourceHandler;
  }

  StateHandler stateHandler = Mockito.mock(StateHandler.class);

  @MockBean(StateHandler.class)
  @Replaces(StateHandler.class)
  StateHandler mStateHandler() {
    return stateHandler;
  }

  WebBackendConnectionsHandler webBackendConnectionsHandler = Mockito.mock(WebBackendConnectionsHandler.class);

  @MockBean(WebBackendConnectionsHandler.class)
  @Replaces(WebBackendConnectionsHandler.class)
  WebBackendConnectionsHandler mWebBackendConnectionsHandler() {
    return webBackendConnectionsHandler;
  }

  WebBackendGeographiesHandler webBackendGeographiesHandler = Mockito.mock(WebBackendGeographiesHandler.class);

  @MockBean(WebBackendGeographiesHandler.class)
  @Replaces(WebBackendGeographiesHandler.class)
  WebBackendGeographiesHandler mWebBackendGeographiesHandler() {
    return webBackendGeographiesHandler;
  }

  WebBackendCheckUpdatesHandler webBackendCheckUpdatesHandler = Mockito.mock(WebBackendCheckUpdatesHandler.class);

  @MockBean(WebBackendCheckUpdatesHandler.class)
  @Replaces(WebBackendCheckUpdatesHandler.class)
  WebBackendCheckUpdatesHandler mWebBackendCheckUpdatesHandler() {
    return webBackendCheckUpdatesHandler;
  }

  WorkspacesHandler workspacesHandler = Mockito.mock(WorkspacesHandler.class);

  @MockBean(WorkspacesHandler.class)
  @Replaces(WorkspacesHandler.class)
  WorkspacesHandler mWorkspacesHandler() {
    return workspacesHandler;
  }

  @MockBean(SynchronousSchedulerClient.class)
  @Replaces(SynchronousSchedulerClient.class)
  SynchronousSchedulerClient mSynchronousSchedulerClient() {
    return Mockito.mock(SynchronousSchedulerClient.class);
  }

  @MockBean(Database.class)
  @Replaces(Database.class)
  @Named("configDatabase")
  Database mDatabase() {
    return Mockito.mock(Database.class);
  }

  @MockBean(DataSource.class)
  @Replaces(DataSource.class)
  DataSource mDataSource() {
    return Mockito.mock(DataSource.class);
  }

  @MockBean(TrackingClient.class)
  @Replaces(TrackingClient.class)
  TrackingClient mTrackingClient() {
    return Mockito.mock(TrackingClient.class);
  }

  @MockBean(WorkflowClient.class)
  @Replaces(WorkflowClient.class)
  WorkflowClient mWorkflowClient() {
    return Mockito.mock(WorkflowClient.class);
  }

  @MockBean(WorkflowServiceStubs.class)
  @Replaces(WorkflowServiceStubs.class)
  WorkflowServiceStubs mWorkflowServiceStubs() {
    return Mockito.mock(WorkflowServiceStubs.class);
  }

  @MockBean(TemporalClient.class)
  @Replaces(TemporalClient.class)
  TemporalClient mTemporalClient() {
    return Mockito.mock(TemporalClient.class);
  }

  @Replaces(DSLContext.class)
  @Named("config")
  DSLContext mDSLContext() {
    return Mockito.mock(DSLContext.class);
  }

  @Inject
  HealthApiController healthApiController;

  @Inject
  EmbeddedServer embeddedServer;

  @Inject
  @Client("/")
  HttpClient client;

  void testEndpointStatus(final HttpRequest request, final HttpStatus expectedStatus) {
    assertEquals(expectedStatus, client.toBlocking().exchange(request).getStatus());
  }

  void testErrorEndpointStatus(final HttpRequest request, final HttpStatus expectedStatus) {
    Assertions.assertThatThrownBy(() -> client.toBlocking().exchange(request))
        .isInstanceOf(HttpClientResponseException.class)
        .asInstanceOf(new InstanceOfAssertFactory(HttpClientResponseException.class, Assertions::assertThat))
        .has(new Condition<HttpClientResponseException>(exception -> exception.getStatus() == expectedStatus,
            "Http status to be %s", expectedStatus));
  }

}
