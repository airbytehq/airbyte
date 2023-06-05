/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import datadog.trace.api.Trace;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions.Procedure;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.util.ApmTraceUtils;
import io.airbyte.integrations.util.ConnectorExceptionUtil;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import org.apache.commons.lang3.ThreadUtils;
import org.apache.commons.lang3.concurrent.BasicThreadFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Accepts EITHER a destination or a source. Routes commands from the commandline to the appropriate
 * methods on the integration. Keeps itself DRY for methods that are common between source and
 * destination.
 */
public class IntegrationRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(IntegrationRunner.class);

  public static final int INTERRUPT_THREAD_DELAY_MINUTES = 60;
  public static final int EXIT_THREAD_DELAY_MINUTES = 70;

  public static final int FORCED_EXIT_CODE = 2;

  private final IntegrationCliParser cliParser;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final Integration integration;
  private final Destination destination;
  private final Source source;
  private static JsonSchemaValidator validator;

  public IntegrationRunner(final Destination destination) {
    this(new IntegrationCliParser(), Destination::defaultOutputRecordCollector, destination, null);
  }

  public IntegrationRunner(final Source source) {
    this(new IntegrationCliParser(), Destination::defaultOutputRecordCollector, null, source);
  }

  @VisibleForTesting
  IntegrationRunner(final IntegrationCliParser cliParser,
                    final Consumer<AirbyteMessage> outputRecordCollector,
                    final Destination destination,
                    final Source source) {
    Preconditions.checkState(destination != null ^ source != null, "can only pass in a destination or a source");
    this.cliParser = cliParser;
    this.outputRecordCollector = outputRecordCollector;
    // integration iface covers the commands that are the same for both source and destination.
    integration = source != null ? source : destination;
    this.source = source;
    this.destination = destination;
    validator = new JsonSchemaValidator();

    Thread.setDefaultUncaughtExceptionHandler(new AirbyteExceptionHandler());
  }

  @VisibleForTesting
  IntegrationRunner(final IntegrationCliParser cliParser,
                    final Consumer<AirbyteMessage> outputRecordCollector,
                    final Destination destination,
                    final Source source,
                    final JsonSchemaValidator jsonSchemaValidator) {
    this(cliParser, outputRecordCollector, destination, source);
    validator = jsonSchemaValidator;
  }

  @Trace(operationName = "RUN_OPERATION")
  public void run(final String[] args) throws Exception {
    final IntegrationConfig parsed = cliParser.parse(args);
    try {
      runInternal(parsed);
    } catch (final Exception e) {
      throw e;
    }
  }

  private void runInternal(final IntegrationConfig parsed) throws Exception {
    LOGGER.info("Running integration: {}", integration.getClass().getName());
    LOGGER.info("Command: {}", parsed.getCommand());
    LOGGER.info("Integration config: {}", parsed);

    try {
      switch (parsed.getCommand()) {
        // common
        case SPEC -> outputRecordCollector.accept(new AirbyteMessage().withType(Type.SPEC).withSpec(integration.spec()));
        case CHECK -> {
          final JsonNode config = parseConfig(parsed.getConfigPath());
          try {
            validateConfig(integration.spec().getConnectionSpecification(), config, "CHECK");
          } catch (final Exception e) {
            // if validation fails don't throw an exception, return a failed connection check message
            outputRecordCollector.accept(new AirbyteMessage().withType(Type.CONNECTION_STATUS).withConnectionStatus(
                new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage(e.getMessage())));
          }

          outputRecordCollector.accept(new AirbyteMessage().withType(Type.CONNECTION_STATUS).withConnectionStatus(integration.check(config)));
        }
        // source only
        case DISCOVER -> {
          final JsonNode config = parseConfig(parsed.getConfigPath());
          validateConfig(integration.spec().getConnectionSpecification(), config, "DISCOVER");
          outputRecordCollector.accept(new AirbyteMessage().withType(Type.CATALOG).withCatalog(source.discover(config)));
        }
        // todo (cgardens) - it is incongruous that that read and write return airbyte message (the
        // envelope) while the other commands return what goes inside it.
        case READ -> {
          final JsonNode config = parseConfig(parsed.getConfigPath());
          validateConfig(integration.spec().getConnectionSpecification(), config, "READ");
          final ConfiguredAirbyteCatalog catalog = parseConfig(parsed.getCatalogPath(), ConfiguredAirbyteCatalog.class);
          final Optional<JsonNode> stateOptional = parsed.getStatePath().map(IntegrationRunner::parseConfig);
          try (final AutoCloseableIterator<AirbyteMessage> messageIterator = source.read(config, catalog, stateOptional.orElse(null))) {
            produceMessages(messageIterator);
          }
        }
        // destination only
        case WRITE -> {
          final JsonNode config = parseConfig(parsed.getConfigPath());
          validateConfig(integration.spec().getConnectionSpecification(), config, "WRITE");
          final ConfiguredAirbyteCatalog catalog = parseConfig(parsed.getCatalogPath(), ConfiguredAirbyteCatalog.class);

          final Procedure consumeWriteStreamCallable = () -> {
            try (final SerializedAirbyteMessageConsumer consumer = destination.getSerializedMessageConsumer(config, catalog, outputRecordCollector)) {
              consumeWriteStream(consumer);
            }
          };

          watchForOrphanThreads(
              consumeWriteStreamCallable,
              () -> System.exit(FORCED_EXIT_CODE),
              INTERRUPT_THREAD_DELAY_MINUTES,
              TimeUnit.MINUTES,
              EXIT_THREAD_DELAY_MINUTES,
              TimeUnit.MINUTES);
        }
        default -> throw new IllegalStateException("Unexpected value: " + parsed.getCommand());
      }
    } catch (final Exception e) {
      // Many of the exceptions thrown are nested inside layers of RuntimeExceptions. An attempt is made
      // to
      // find the root exception that corresponds to a configuration error. If that does not exist, we
      // just return the original exception.
      ApmTraceUtils.addExceptionToTrace(e);
      final Throwable rootThrowable = ConnectorExceptionUtil.getRootConfigError(e);
      final String displayMessage = ConnectorExceptionUtil.getDisplayMessage(rootThrowable);
      // If the source connector throws a config error, a trace message with the relevant message should
      // be surfaced.
      if (ConnectorExceptionUtil.isConfigError(rootThrowable)) {
        AirbyteTraceMessageUtility.emitConfigErrorTrace(e, displayMessage);
      }
      if (parsed.getCommand().equals(Command.CHECK)) {
        // Currently, special handling is required for the CHECK case since the user display information in
        // the trace message is
        // not properly surfaced to the FE. In the future, we can remove this and just throw an exception.
        outputRecordCollector
            .accept(
                new AirbyteMessage()
                    .withType(Type.CONNECTION_STATUS)
                    .withConnectionStatus(
                        new AirbyteConnectionStatus()
                            .withStatus(AirbyteConnectionStatus.Status.FAILED)
                            .withMessage(displayMessage)));
        return;
      }
      throw e;
    }

    LOGGER.info("Completed integration: {}", integration.getClass().getName());
  }

  private void produceMessages(final AutoCloseableIterator<AirbyteMessage> messageIterator) throws Exception {
    watchForOrphanThreads(
        () -> messageIterator.forEachRemaining(outputRecordCollector),
        () -> System.exit(FORCED_EXIT_CODE),
        INTERRUPT_THREAD_DELAY_MINUTES,
        TimeUnit.MINUTES,
        EXIT_THREAD_DELAY_MINUTES,
        TimeUnit.MINUTES);
  }

  @VisibleForTesting
  static void consumeWriteStream(final SerializedAirbyteMessageConsumer consumer) throws Exception {
    try (final BufferedInputStream bis = new BufferedInputStream(System.in);
        final ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
      consumeWriteStream(consumer, bis, baos);
    }
  }

  @VisibleForTesting
  static void consumeWriteStream(final SerializedAirbyteMessageConsumer consumer,
                                 final BufferedInputStream bis,
                                 final ByteArrayOutputStream baos)
      throws Exception {
    consumer.start();

    final byte[] buffer = new byte[8192]; // 8K buffer
    int bytesRead;
    boolean lastWasNewLine = false;

    while ((bytesRead = bis.read(buffer)) != -1) {
      for (int i = 0; i < bytesRead; i++) {
        final byte b = buffer[i];
        if (b == '\n' || b == '\r') {
          if (!lastWasNewLine && baos.size() > 0) {
            consumer.accept(baos.toString(StandardCharsets.UTF_8), baos.size());
            baos.reset();
          }
          lastWasNewLine = true;
        } else {
          baos.write(b);
          lastWasNewLine = false;
        }
      }
    }

    // Handle last line if there's one
    if (baos.size() > 0) {
      consumer.accept(baos.toString(StandardCharsets.UTF_8), baos.size());
    }
  }

  /**
   * This method calls a runMethod and make sure that it won't produce orphan non-daemon active
   * threads once it is done. Active non-daemon threads blocks JVM from exiting when the main thread
   * is done, whereas daemon ones don't.
   * <p>
   * If any active non-daemon threads would be left as orphans, this method will schedule some
   * interrupt/exit hooks after giving it some time delay to close up properly. It is generally
   * preferred to have a proper closing sequence from children threads instead of interrupting or
   * force exiting the process, so this mechanism serve as a fallback while surfacing warnings in logs
   * for maintainers to fix the code behavior instead.
   */
  @VisibleForTesting
  static void watchForOrphanThreads(final Procedure runMethod,
                                    final Runnable exitHook,
                                    final int interruptTimeDelay,
                                    final TimeUnit interruptTimeUnit,
                                    final int exitTimeDelay,
                                    final TimeUnit exitTimeUnit)
      throws Exception {
    final Thread currentThread = Thread.currentThread();
    try {
      runMethod.call();
    } finally {
      final List<Thread> runningThreads = ThreadUtils.getAllThreads()
          .stream()
          // daemon threads don't block the JVM if the main `currentThread` exits, so they are not problematic
          .filter(runningThread -> !runningThread.getName().equals(currentThread.getName()) && !runningThread.isDaemon())
          .toList();
      if (!runningThreads.isEmpty()) {
        LOGGER.warn("""
                    The main thread is exiting while children non-daemon threads from a connector are still active.
                    Ideally, this situation should not happen...
                    Please check with maintainers if the connector or library code should safely clean up its threads before quitting instead.
                    The main thread is: {}""", dumpThread(currentThread));
        final ScheduledExecutorService scheduledExecutorService = Executors
            .newSingleThreadScheduledExecutor(new BasicThreadFactory.Builder()
                // this thread executor will create daemon threads, so it does not block exiting if all other active
                // threads are already stopped.
                .daemon(true).build());
        for (final Thread runningThread : runningThreads) {
          final String str = "Active non-daemon thread: " + dumpThread(runningThread);
          LOGGER.warn(str);
          // even though the main thread is already shutting down, we still leave some chances to the children
          // threads to close properly on their own.
          // So, we schedule an interrupt hook after a fixed time delay instead...
          scheduledExecutorService.schedule(runningThread::interrupt, interruptTimeDelay, interruptTimeUnit);
        }
        scheduledExecutorService.schedule(() -> {
          if (ThreadUtils.getAllThreads().stream()
              .anyMatch(runningThread -> !runningThread.isDaemon() && !runningThread.getName().equals(currentThread.getName()))) {
            LOGGER.error("Failed to interrupt children non-daemon threads, forcefully exiting NOW...\n");
            exitHook.run();
          }
        }, exitTimeDelay, exitTimeUnit);
      }
    }
  }

  private static String dumpThread(final Thread thread) {
    return String.format("%s (%s)\n Thread stacktrace: %s", thread.getName(), thread.getState(),
        Strings.join(List.of(thread.getStackTrace()), "\n        at "));
  }

  private static void validateConfig(final JsonNode schemaJson, final JsonNode objectJson, final String operationType) throws Exception {
    final Set<String> validationResult = validator.validate(schemaJson, objectJson);
    if (!validationResult.isEmpty()) {
      throw new Exception(String.format("Verification error(s) occurred for %s. Errors: %s ",
          operationType, validationResult));
    }
  }

  private static JsonNode parseConfig(final Path path) {
    return Jsons.deserialize(IOs.readFile(path));
  }

  private static <T> T parseConfig(final Path path, final Class<T> klass) {
    final JsonNode jsonNode = parseConfig(path);
    return Jsons.object(jsonNode, klass);
  }

  /**
   * @param connectorImage Expected format: [organization/]image[:version]
   */
  @VisibleForTesting
  static String parseConnectorVersion(final String connectorImage) {
    if (connectorImage == null || connectorImage.equals("")) {
      return "unknown";
    }

    final String[] tokens = connectorImage.split(":");
    return tokens[tokens.length - 1];
  }

}
