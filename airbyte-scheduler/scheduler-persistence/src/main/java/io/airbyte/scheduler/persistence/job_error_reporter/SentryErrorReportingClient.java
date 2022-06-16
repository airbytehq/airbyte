/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardWorkspace;
import io.sentry.Sentry;
import io.sentry.SentryEvent;
import io.sentry.protocol.Message;
import io.sentry.protocol.SentryException;
import io.sentry.protocol.SentryId;
import io.sentry.protocol.SentryStackFrame;
import io.sentry.protocol.SentryStackTrace;
import io.sentry.protocol.User;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SentryErrorReportingClient implements ErrorReportingClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(LoggingErrorReportingClient.class);

  public SentryErrorReportingClient() {
    LOGGER.info("INITIALIZE SENTRY");
    Sentry.init(options -> {
      options.setDsn(""); // TODO get this from ENV / config
      options.setEnableUncaughtExceptionHandler(false);
    });
  }

  @Override
  public void report(final StandardWorkspace workspace, final FailureReason failureReason, final String dockerImage,
      final Map<String, String> metadata) {
    LOGGER.info("REPORT FAILURE TO SENTRY");
    final SentryEvent event = new SentryEvent();

    // airbyte/source-xyz:1.2.0 -> source-xyz@1.2.0
    final String release = dockerImage.replace(":", "@").substring(dockerImage.lastIndexOf("/") + 1);
    event.setRelease(release);

    // TODO change fingerprint so it separates on different connectors
//    final Optional<String> connectorSlug = Arrays.stream(release.split(":")).findFirst();

    // set workspace as the user in sentry to get impact and priority
    final User sentryUser = new User();
    sentryUser.setId(String.valueOf(workspace.getWorkspaceId()));
    sentryUser.setUsername(workspace.getName());
    event.setUser(sentryUser);

    // set metadata as tags
    event.setTags(metadata);

    final Message message = new Message();
    message.setFormatted(failureReason.getInternalMessage());
    event.setMessage(message);

    // don't attach current thread stacktrace to the event
    event.setThreads(new ArrayList<>());
    event.setPlatform("other");

    // attach failure reason stack trace
    final List<SentryException> parsedExceptions = buildSentryExceptions(failureReason.getStacktrace());
    event.setExceptions(parsedExceptions);

    Sentry.withScope(scope -> {
      final Map<String, String> failureReasonContext = new HashMap<>();
      failureReasonContext.put("internalMessage", failureReason.getInternalMessage());
      failureReasonContext.put("externalMessage", failureReason.getExternalMessage());
      failureReasonContext.put("stacktrace", failureReason.getStacktrace());
      scope.setContexts("Failure Reason", failureReasonContext);

      final SentryId eventId = Sentry.captureEvent(event);
      LOGGER.info("SENT SENTRY EVENT: {}", eventId);
    });
  }

  private List<SentryException> buildSentryExceptions(final String stacktrace) {
    // Stack trace parsing should be done on a best-effort basis
    // if we encounter something complex or an unsupported language, we'll fall back to message-based grouping instead
    return Exceptions.swallowWithDefault(() -> {
      if (stacktrace.startsWith("Traceback (most recent call last):")) {
        return buildPythonSentryExceptions(stacktrace);
      }
      if (stacktrace.contains(".java")) {
        return buildJavaSentryExceptions(stacktrace);
      }

      return null;
    }, null);
  }

  private List<SentryException> buildPythonSentryExceptions(final String stacktrace) {
    // TODO
    return null;
  }

  private List<SentryException> buildJavaSentryExceptions(final String stacktrace) {
    // TODO
    return null;
  }

}
