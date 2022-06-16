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
    final List<SentryException> sentryExceptions = new ArrayList<>();
    final String[] exceptions = stacktrace.split("\n\n"); // chained exceptions are separated by two new lines

    for (final String exceptionStr : exceptions) {
      final SentryStackTrace stackTrace = new SentryStackTrace();
      final List<SentryStackFrame> stackFrames = new ArrayList<>();

      // Use a regex to grab stack trace frame information
      final Pattern framePattern = Pattern.compile("File \"(?<absPath>.+)\", line (?<lineno>[0-9]+), in (?<function>.+)\\n {4}(?<contextLine>.+)\\n");
      final Matcher matcher = framePattern.matcher(exceptionStr);
      int lastMatchIdx = -1;

      while (matcher.find()) {
        final String absPath = matcher.group("absPath");
        final String lineno = matcher.group("lineno");
        final String function = matcher.group("function");
        final String contextLine = matcher.group("contextLine");

        final SentryStackFrame stackFrame = new SentryStackFrame();
        stackFrame.setAbsPath(absPath);
        stackFrame.setLineno(Integer.valueOf(lineno));
        stackFrame.setFunction(function);
        stackFrame.setContextLine(contextLine);
        stackFrames.add(stackFrame);

        lastMatchIdx = matcher.end();
      }

      if (stackFrames.size() > 0) {
        stackTrace.setFrames(stackFrames);

        final SentryException sentryException = new SentryException();
        sentryException.setStacktrace(stackTrace);

        // The final part of our stack trace has the exception type and (optionally) a value (e.g. "RuntimeError: This is the value")
        final String remaining = exceptionStr.substring(lastMatchIdx);
        final String[] parts = remaining.split(":", 2);

        if (parts.length > 0) {
          sentryException.setType(parts[0]);
          if (parts.length == 2) {
            sentryException.setValue(parts[1]);
          }

          sentryExceptions.add(sentryException);
        }
      }
    }

    return sentryExceptions;
  }

  private List<SentryException> buildJavaSentryExceptions(final String stacktrace) {
    // TODO
    return null;
  }

}
