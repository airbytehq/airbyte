/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions.Procedure;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.WorkerEnvConstants;
import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.sentry.ITransaction;
import io.sentry.NoOpTransaction;
import io.sentry.Sentry;
import io.sentry.SentryLevel;
import io.sentry.SpanStatus;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Scanner;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
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
    this.integration = source != null ? source : destination;
    this.source = source;
    this.destination = destination;
    validator = new JsonSchemaValidator();
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

  public void run(final String[] args) throws Exception {
    final IntegrationConfig parsed = cliParser.parse(args);
    final ITransaction transaction = createSentryTransaction(integration.getClass(), parsed.getCommand());
    try {
      runInternal(parsed);
      transaction.finish(SpanStatus.OK);
    } catch (final Exception e) {
      transaction.setThrowable(e);
      transaction.finish(SpanStatus.INTERNAL_ERROR);
      throw e;
    } finally {
      /*
       * This finally block may not run, probably because the container can be terminated by the worker.
       * So the transaction should always be finished in the try and catch blocks.
       */
      transaction.finish();
    }
  }

  private void runInternal(final IntegrationConfig parsed) throws Exception {
    LOGGER.info("Running integration: {}", integration.getClass().getName());
    LOGGER.info("Command: {}", parsed.getCommand());
    LOGGER.info("Integration config: {}", parsed);

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
          AirbyteSentry.executeWithTracing("ReadSource", () -> messageIterator.forEachRemaining(outputRecordCollector::accept));
        }
      }
      // destination only
      case WRITE -> {
        final JsonNode config = parseConfig(parsed.getConfigPath());
        validateConfig(integration.spec().getConnectionSpecification(), config, "WRITE");
        final ConfiguredAirbyteCatalog catalog = parseConfig(parsed.getCatalogPath(), ConfiguredAirbyteCatalog.class);
        try (final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, outputRecordCollector)) {
          AirbyteSentry.executeWithTracing("WriteDestination", () -> runConsumer(consumer));
        }
      }
      default -> throw new IllegalStateException("Unexpected value: " + parsed.getCommand());
    }

    LOGGER.info("Completed integration: {}", integration.getClass().getName());
  }

  @VisibleForTesting
  static void consumeWriteStream(final AirbyteMessageConsumer consumer) throws Exception {
    // use a Scanner that only processes new line characters to strictly abide with the
    // https://jsonlines.org/ standard
    final Scanner input = new Scanner(System.in, StandardCharsets.UTF_8).useDelimiter("[\r\n]+");
    consumer.start();
    while (input.hasNext()) {
      final String inputString = input.next();
      final Optional<AirbyteMessage> messageOptional = Jsons.tryDeserialize(inputString, AirbyteMessage.class);
      if (messageOptional.isPresent()) {
        consumer.accept(messageOptional.get());
      } else {
        LOGGER.error("Received invalid message: " + inputString);
      }
    }
  }

  private static void runConsumer(final AirbyteMessageConsumer consumer) throws Exception {
    watchForOrphanThreads(
        () -> consumeWriteStream(consumer),
        () -> System.exit(FORCED_EXIT_CODE),
        INTERRUPT_THREAD_DELAY_MINUTES,
        TimeUnit.MINUTES,
        EXIT_THREAD_DELAY_MINUTES,
        TimeUnit.MINUTES);
  }

  /**
   * This method calls a runMethod and make sure that it won't produce orphan non-daemon active
   * threads once it is done. Active non-daemon threads blocks JVM from exiting when the main thread
   * is done, whereas daemon ones don't.
   *
   * If any active non-daemon threads would be left as orphans, this method will schedule some
   * interrupt/exit hooks after giving it some time delay to close up properly. It is generally
   * preferred to have a proper closing sequence from children threads instead of interrupting or
   * force exiting the process, so this mechanism serve as a fallback while surfacing warnings in logs
   * and sentry for maintainers to fix the code behavior instead.
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
          .collect(Collectors.toList());
      if (!runningThreads.isEmpty()) {
        final StringBuilder sentryMessageBuilder = new StringBuilder();
        LOGGER.warn("""
                    The main thread is exiting while children non-daemon threads from a connector are still active.
                    Ideally, this situation should not happen...
                    Please check with maintainers if the connector or library code should safely clean up its threads before quitting instead.
                    The main thread is: {}""", dumpThread(currentThread));
        sentryMessageBuilder.append("The main thread is exiting while children non-daemon threads are still active.\nMain Thread:")
            .append(dumpThread(currentThread));
        final ScheduledExecutorService scheduledExecutorService = Executors
            .newSingleThreadScheduledExecutor(new BasicThreadFactory.Builder()
                // this thread executor will create daemon threads, so it does not block exiting if all other active
                // threads are already stopped.
                .daemon(true).build());
        for (final Thread runningThread : runningThreads) {
          final String str = "Active non-daemon thread: " + dumpThread(runningThread);
          LOGGER.warn(str);
          sentryMessageBuilder.append(str);
          // even though the main thread is already shutting down, we still leave some chances to the children
          // threads to close properly on their own.
          // So, we schedule an interrupt hook after a fixed time delay instead...
          scheduledExecutorService.schedule(runningThread::interrupt, interruptTimeDelay, interruptTimeUnit);
        }
        Sentry.captureMessage(sentryMessageBuilder.toString(), SentryLevel.WARNING);
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

  private static ITransaction createSentryTransaction(final Class<?> connectorClass, final Command command) {
    if (command == Command.SPEC) {
      return NoOpTransaction.getInstance();
    }

    final Map<String, String> env = System.getenv();
    final boolean enableSentry = Boolean.parseBoolean(env.getOrDefault("ENABLE_SENTRY", "false"));
    final String sentryDsn = env.getOrDefault("SENTRY_DSN", "");
    if (!enableSentry || sentryDsn.equals("")) {
      LOGGER.debug("Skip Sentry transaction because DSN is not available");
      return NoOpTransaction.getInstance();
    }

    final String version = parseConnectorVersion(env.getOrDefault("WORKER_CONNECTOR_IMAGE", ""));
    final String airbyteVersion = env.getOrDefault(EnvConfigs.AIRBYTE_VERSION, "");
    final String airbyteRole = env.getOrDefault(EnvConfigs.AIRBYTE_ROLE, "");
    final boolean isDev = version.startsWith(AirbyteVersion.DEV_VERSION_PREFIX)
        || airbyteVersion.startsWith(AirbyteVersion.DEV_VERSION_PREFIX)
        || airbyteRole.equals("airbyter");
    if (isDev) {
      LOGGER.debug("Skip Sentry transaction for dev environment");
      return NoOpTransaction.getInstance();
    }
    final String connector = env.getOrDefault("APPLICATION", "");
    if (connector.equals("")) {
      LOGGER.debug("Skip Sentry transaction for unknown connector");
      return NoOpTransaction.getInstance();
    }
    final String workerEnvironment = env.getOrDefault("WORKER_ENVIRONMENT", "");
    final String workerJobId = env.getOrDefault(WorkerEnvConstants.WORKER_JOB_ID, "");
    final String workerJobAttempt = env.getOrDefault(WorkerEnvConstants.WORKER_JOB_ATTEMPT, "");
    if (workerEnvironment.equals("") || workerEnvironment.equals(WorkerEnvironment.DOCKER.name())) {
      LOGGER.debug("Skip Sentry transaction for unknown or docker deployment");
      return NoOpTransaction.getInstance();
    }

    // https://docs.sentry.io/platforms/java/configuration/
    Sentry.init(options -> {
      options.setDsn(sentryDsn);
      options.setEnableExternalConfiguration(true);
      options.setTracesSampleRate(1.0);
      options.setRelease(String.format("%s@%s", connector, version));
      options.setEnvironment(isDev ? "dev" : "production");
      options.setTag("connector", connector);
      options.setTag("connector_version", version);
      options.setTag("job_id", workerJobId);
      options.setTag("job_attempt", workerJobAttempt);
      options.setTag("airbyte_version", airbyteVersion);
      options.setTag("worker_environment", workerEnvironment);
    });

    final ITransaction transaction = Sentry.startTransaction(
        connectorClass.getSimpleName(),
        command.toString(),
        true);
    LOGGER.info("Sentry transaction event: {}", transaction.getEventId());
    return transaction;
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
