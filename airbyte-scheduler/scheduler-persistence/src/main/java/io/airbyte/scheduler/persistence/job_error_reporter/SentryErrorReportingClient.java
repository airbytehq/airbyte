/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardWorkspace;
import io.sentry.Sentry;
import io.sentry.SentryEvent;
import io.sentry.protocol.Message;
import io.sentry.protocol.SentryException;
import io.sentry.protocol.SentryId;
import io.sentry.protocol.User;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
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
    final SentryEvent event = new SentryEvent();

    // airbyte/source-xyz:1.2.0 -> source-xyz@1.2.0
    final String release = dockerImage.replace(":", "@").substring(dockerImage.lastIndexOf("/") + 1);
    event.setRelease(release);

    // add connector to event fingerprint to ensure separate grouping per connector
    final String[] releaseParts = release.split("@");
    if (releaseParts.length > 0) {
      event.setFingerprints(List.of("{{ default }}", releaseParts[0]));
    }

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
    final String failureStackTrace = failureReason.getStacktrace();
    if (failureStackTrace != null) {
      final List<SentryException> parsedExceptions = SentryExceptionHelper.buildSentryExceptions(failureStackTrace);
      event.setExceptions(parsedExceptions);
    }

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
}
