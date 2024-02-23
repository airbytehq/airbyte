/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import datadog.trace.api.Trace;
import io.airbyte.cdk.integrations.util.ApmTraceUtils;
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil;
import io.airbyte.cdk.integrations.util.concurrent.ConcurrentStreamConsumer;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.StreamStatusUtils;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.function.Predicate;
import java.util.stream.Collectors;
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

  public static final String TYPE_AND_DEDUPE_THREAD_NAME = "type-and-dedupe";

  /**
   * Filters threads that should not be considered when looking for orphaned threads at shutdown of
   * the integration runner.
   * <p>
   * </p>
   * <b>N.B.</b> Daemon threads don't block the JVM if the main `currentThread` exits, so they are not
   * problematic. Additionally, ignore database connection pool threads, which stay active so long as
   * the database connection pool is open.
   */
  @VisibleForTesting
  static final Predicate<Thread> ORPHANED_THREAD_FILTER = runningThread -> !runningThread.getName().equals(Thread.currentThread().getName())
      && !runningThread.isDaemon() && !TYPE_AND_DEDUPE_THREAD_NAME.equals(runningThread.getName());

  public static final int INTERRUPT_THREAD_DELAY_MINUTES = 60;
  public static final int EXIT_THREAD_DELAY_MINUTES = 70;

  public static final int FORCED_EXIT_CODE = 2;

  private static final Runnable EXIT_HOOK = () -> System.exit(FORCED_EXIT_CODE);

  private final IntegrationCliParser cliParser;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final Integration integration;
  private final Destination destination;
  private final Source source;
  private final FeatureFlags featureFlags;
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
    this.featureFlags = new EnvVariableFeatureFlags();
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
          if (integration instanceof Destination) {
            DestinationConfig.initialize(config, ((Destination) integration).isV2Destination());
          }
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
          try {
            if (featureFlags.concurrentSourceStreamRead()) {
              LOGGER.info("Concurrent source stream read enabled.");
              readConcurrent(config, catalog, stateOptional);
            } else {
              readSerial(config, catalog, stateOptional);
            }
          } finally {
            if (source instanceof AutoCloseable) {
              ((AutoCloseable) source).close();
            }
          }
        }
        // destination only
        case WRITE -> {
          final JsonNode config = parseConfig(parsed.getConfigPath());
          validateConfig(integration.spec().getConnectionSpecification(), config, "WRITE");
          // save config to singleton
          DestinationConfig.initialize(config, ((Destination) integration).isV2Destination());
          final ConfiguredAirbyteCatalog catalog = parseConfig(parsed.getCatalogPath(), ConfiguredAirbyteCatalog.class);

          try (final SerializedAirbyteMessageConsumer consumer = destination.getSerializedMessageConsumer(config, catalog, outputRecordCollector)) {
            consumeWriteStream(consumer);
          } finally {
            stopOrphanedThreads(EXIT_HOOK,
                INTERRUPT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
                EXIT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES);
          }
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

  private void produceMessages(final AutoCloseableIterator<AirbyteMessage> messageIterator, final Consumer<AirbyteMessage> recordCollector) {
    messageIterator.getAirbyteStream().ifPresent(s -> LOGGER.debug("Producing messages for stream {}...", s));
    messageIterator.forEachRemaining(recordCollector);
    messageIterator.getAirbyteStream().ifPresent(s -> LOGGER.debug("Finished producing messages for stream {}..."));
  }

  private void readConcurrent(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final Optional<JsonNode> stateOptional)
      throws Exception {
    final Collection<AutoCloseableIterator<AirbyteMessage>> streams = source.readStreams(config, catalog, stateOptional.orElse(null));

    try (final ConcurrentStreamConsumer streamConsumer = new ConcurrentStreamConsumer(this::consumeFromStream, streams.size())) {
      /*
       * Break the streams into partitions equal to the number of concurrent streams supported by the
       * stream consumer.
       */
      final Integer partitionSize = streamConsumer.getParallelism();
      final List<List<AutoCloseableIterator<AirbyteMessage>>> partitions = Lists.partition(streams.stream().toList(),
          partitionSize);

      // Submit each stream partition for concurrent execution
      partitions.forEach(partition -> {
        streamConsumer.accept(partition);
      });

      // Check for any exceptions that were raised during the concurrent execution
      if (streamConsumer.getException().isPresent()) {
        throw streamConsumer.getException().get();
      }
    } catch (final Exception e) {
      LOGGER.error("Unable to perform concurrent read.", e);
      throw e;
    } finally {
      stopOrphanedThreads(EXIT_HOOK,
          INTERRUPT_THREAD_DELAY_MINUTES,
          TimeUnit.MINUTES,
          EXIT_THREAD_DELAY_MINUTES,
          TimeUnit.MINUTES);
    }
  }

  private void readSerial(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final Optional<JsonNode> stateOptional) throws Exception {
    try (final AutoCloseableIterator<AirbyteMessage> messageIterator = source.read(config, catalog, stateOptional.orElse(null))) {
      produceMessages(messageIterator, outputRecordCollector);
    } finally {
      stopOrphanedThreads(EXIT_HOOK,
          INTERRUPT_THREAD_DELAY_MINUTES,
          TimeUnit.MINUTES,
          EXIT_THREAD_DELAY_MINUTES,
          TimeUnit.MINUTES);
    }
  }

  private void consumeFromStream(final AutoCloseableIterator<AirbyteMessage> stream) {
    try {
      final Consumer<AirbyteMessage> streamStatusTrackingRecordConsumer = StreamStatusUtils.statusTrackingRecordCollector(stream,
          outputRecordCollector, Optional.of(AirbyteTraceMessageUtility::emitStreamStatusTrace));
      produceMessages(stream, streamStatusTrackingRecordConsumer);
    } catch (final Exception e) {
      stream.getAirbyteStream().ifPresent(s -> LOGGER.error("Failed to consume from stream {}.", s, e));
      throw new RuntimeException(e);
    }
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
   * Stops any non-daemon threads that could block the JVM from exiting when the main thread is done.
   * <p>
   * If any active non-daemon threads would be left as orphans, this method will schedule some
   * interrupt/exit hooks after giving it some time delay to close up properly. It is generally
   * preferred to have a proper closing sequence from children threads instead of interrupting or
   * force exiting the process, so this mechanism serve as a fallback while surfacing warnings in logs
   * for maintainers to fix the code behavior instead.
   *
   * @param exitHook The {@link Runnable} exit hook to execute for any orphaned threads.
   * @param interruptTimeDelay The time to delay execution of the orphaned thread interrupt attempt.
   * @param interruptTimeUnit The time unit of the interrupt delay.
   * @param exitTimeDelay The time to delay execution of the orphaned thread exit hook.
   * @param exitTimeUnit The time unit of the exit delay.
   */
  @VisibleForTesting
  static void stopOrphanedThreads(final Runnable exitHook,
                                  final int interruptTimeDelay,
                                  final TimeUnit interruptTimeUnit,
                                  final int exitTimeDelay,
                                  final TimeUnit exitTimeUnit) {
    final Thread currentThread = Thread.currentThread();

    final List<Thread> runningThreads = ThreadUtils.getAllThreads()
        .stream()
        .filter(ORPHANED_THREAD_FILTER)
        .collect(Collectors.toList());
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

  public static JsonNode parseConfig(final Path path) {
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
