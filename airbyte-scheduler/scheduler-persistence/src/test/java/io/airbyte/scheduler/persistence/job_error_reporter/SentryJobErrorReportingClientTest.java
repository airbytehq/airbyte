/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import static io.airbyte.scheduler.persistence.job_error_reporter.SentryJobErrorReportingClient.STACKTRACE_PARSE_ERROR_TAG_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.FailureReason.FailureType;
import io.airbyte.config.StandardWorkspace;
import io.sentry.IHub;
import io.sentry.NoOpHub;
import io.sentry.SentryEvent;
import io.sentry.protocol.Message;
import io.sentry.protocol.SentryException;
import io.sentry.protocol.User;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

public class SentryJobErrorReportingClientTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final String WORKSPACE_NAME = "My Workspace";
  private static final String DOCKER_IMAGE = "airbyte/source-stripe:1.2.3";

  private final StandardWorkspace workspace = new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withName(WORKSPACE_NAME);
  private SentryJobErrorReportingClient sentryErrorReportingClient;
  private IHub mockSentryHub;
  private SentryExceptionHelper mockSentryExceptionHelper;

  @BeforeEach
  void setup() {
    mockSentryHub = mock(IHub.class);
    mockSentryExceptionHelper = mock(SentryExceptionHelper.class);
    sentryErrorReportingClient = new SentryJobErrorReportingClient(mockSentryHub, mockSentryExceptionHelper);
  }

  @Test
  void testCreateSentryHubWithBlankDSN() {
    final String sentryDSN = "";
    final IHub sentryHub = SentryJobErrorReportingClient.createSentryHubWithDSN(sentryDSN);
    assertEquals(NoOpHub.getInstance(), sentryHub);
  }

  @Test
  void testCreateSentryHubWithNullDSN() {
    final IHub sentryHub = SentryJobErrorReportingClient.createSentryHubWithDSN(null);
    assertEquals(NoOpHub.getInstance(), sentryHub);
  }

  @Test
  void testCreateSentryHubWithDSN() {
    final String sentryDSN = "https://public@sentry.example.com/1";
    final IHub sentryHub = SentryJobErrorReportingClient.createSentryHubWithDSN(sentryDSN);
    assertNotNull(sentryHub);
    assertEquals(sentryDSN, sentryHub.getOptions().getDsn());
    assertFalse(sentryHub.getOptions().isAttachStacktrace());
    assertFalse(sentryHub.getOptions().isEnableUncaughtExceptionHandler());
  }

  @Test
  void testReportJobFailureReason() {
    final ArgumentCaptor<SentryEvent> eventCaptor = ArgumentCaptor.forClass(SentryEvent.class);

    final FailureReason failureReason = new FailureReason()
        .withFailureOrigin(FailureOrigin.SOURCE)
        .withFailureType(FailureType.SYSTEM_ERROR)
        .withInternalMessage("RuntimeError: Something went wrong");
    final Map<String, String> metadata = Map.of("some_metadata", "some_metadata_value");

    sentryErrorReportingClient.reportJobFailureReason(workspace, failureReason, DOCKER_IMAGE, metadata);

    verify(mockSentryHub).captureEvent(eventCaptor.capture());
    final SentryEvent actualEvent = eventCaptor.getValue();
    assertEquals("other", actualEvent.getPlatform());
    assertEquals("airbyte-source-stripe@1.2.3", actualEvent.getRelease());
    assertEquals(List.of("{{ default }}", "airbyte-source-stripe"), actualEvent.getFingerprints());
    assertEquals("some_metadata_value", actualEvent.getTag("some_metadata"));
    assertNull(actualEvent.getTag(STACKTRACE_PARSE_ERROR_TAG_KEY));
    assertNull(actualEvent.getExceptions());

    final User sentryUser = actualEvent.getUser();
    assertNotNull(sentryUser);
    assertEquals(WORKSPACE_ID.toString(), sentryUser.getId());
    assertEquals(WORKSPACE_NAME, sentryUser.getUsername());

    final Message message = actualEvent.getMessage();
    assertNotNull(message);
    assertEquals("RuntimeError: Something went wrong", message.getFormatted());
  }

  @Test
  void testReportJobFailureReasonWithStacktrace() {
    final ArgumentCaptor<SentryEvent> eventCaptor = ArgumentCaptor.forClass(SentryEvent.class);

    final List<SentryException> exceptions = new ArrayList<>();
    final SentryException exception = new SentryException();
    exception.setType("RuntimeError");
    exception.setValue("Something went wrong");
    exceptions.add(exception);

    when(mockSentryExceptionHelper.buildSentryExceptions("Some valid stacktrace")).thenReturn(Optional.of(exceptions));

    final FailureReason failureReason = new FailureReason()
        .withInternalMessage("RuntimeError: Something went wrong")
        .withStacktrace("Some valid stacktrace");

    sentryErrorReportingClient.reportJobFailureReason(workspace, failureReason, DOCKER_IMAGE, Map.of());

    verify(mockSentryHub).captureEvent(eventCaptor.capture());
    final SentryEvent actualEvent = eventCaptor.getValue();
    assertEquals(exceptions, actualEvent.getExceptions());
    assertNull(actualEvent.getTag(STACKTRACE_PARSE_ERROR_TAG_KEY));
  }

  @Test
  void testReportJobFailureReasonWithInvalidStacktrace() {
    final ArgumentCaptor<SentryEvent> eventCaptor = ArgumentCaptor.forClass(SentryEvent.class);
    final String invalidStacktrace = "Invalid stacktrace\nRuntimeError: Something went wrong";

    when(mockSentryExceptionHelper.buildSentryExceptions(invalidStacktrace)).thenReturn(Optional.empty());

    final FailureReason failureReason = new FailureReason()
        .withInternalMessage("Something went wrong")
        .withStacktrace(invalidStacktrace);

    sentryErrorReportingClient.reportJobFailureReason(workspace, failureReason, DOCKER_IMAGE, Map.of());

    verify(mockSentryHub).captureEvent(eventCaptor.capture());
    final SentryEvent actualEvent = eventCaptor.getValue();
    assertEquals("1", actualEvent.getTag(STACKTRACE_PARSE_ERROR_TAG_KEY));
    final List<SentryException> exceptions = actualEvent.getExceptions();
    assertNotNull(exceptions);
    assertEquals(1, exceptions.size());
    assertEquals("Invalid stacktrace, RuntimeError: ", exceptions.get(0).getValue());
  }

}
