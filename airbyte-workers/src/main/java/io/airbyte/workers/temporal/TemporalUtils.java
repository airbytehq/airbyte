/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import com.uber.m3.tally.RootScopeBuilder;
import com.uber.m3.tally.Scope;
import com.uber.m3.tally.StatsReporter;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.micrometer.core.instrument.MeterRegistry;
import io.micronaut.context.annotation.Property;
import io.temporal.activity.ActivityExecutionContext;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.api.namespace.v1.NamespaceConfig;
import io.temporal.api.namespace.v1.NamespaceInfo;
import io.temporal.api.workflowservice.v1.DescribeNamespaceRequest;
import io.temporal.api.workflowservice.v1.UpdateNamespaceRequest;
import io.temporal.client.ActivityCompletionException;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowStub;
import io.temporal.common.RetryOptions;
import io.temporal.common.reporter.MicrometerClientStatsReporter;
import io.temporal.serviceclient.SimpleSslContextBuilder;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;
import io.temporal.workflow.Functions;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.io.Serializable;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;
import javax.inject.Singleton;
import javax.net.ssl.SSLException;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.time.DurationFormatUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;

@Slf4j
@Singleton
public class TemporalUtils {

  private static final Duration WAIT_INTERVAL = Duration.ofSeconds(2);
  private static final Duration MAX_TIME_TO_CONNECT = Duration.ofMinutes(2);
  private static final Duration WAIT_TIME_AFTER_CONNECT = Duration.ofSeconds(5);
  public static final String DEFAULT_NAMESPACE = "default";
  public static final Duration SEND_HEARTBEAT_INTERVAL = Duration.ofSeconds(10);
  public static final Duration HEARTBEAT_TIMEOUT = Duration.ofSeconds(30);
  public static final RetryOptions NO_RETRY = RetryOptions.newBuilder().setMaximumAttempts(1).build();
  private static final double REPORT_INTERVAL_SECONDS = 120.0;

  private Integer activityNumberOfAttempts;
  private Integer initialDelayBetweenActivityAttemptsSeconds;
  private Integer maxDelayBetweenActivityAttemptsSeconds;
  private String temporalCloudClientCert;
  private String temporalCloudClientKey;
  @Property(name = "temporal.cloud.enabled",
            defaultValue = "false")
  private Boolean temporalCloudEnabled;
  private String temporalCloudHost;
  private String temporalCloudNamespace;
  private String temporalHost;
  private Integer temporalRetentionInDays;

  public TemporalUtils() {}

  public TemporalUtils(@Property(name = "airbyte.activity.max-attempts",
                                 defaultValue = "5") final Integer activityNumberOfAttempts,
                       @Property(name = "airbyte.activity.initial-delay",
                                 defaultValue = "30") final Integer initialDelayBetweenActivityAttemptsSeconds,
                       @Property(name = "airbyte.activity.max-delay",
                                 defaultValue = "600") final Integer maxDelayBetweenActivityAttemptsSeconds,
                       @Property(name = "temporal.cloud.client.cert") final String temporalCloudClientCert,
                       @Property(name = "temporal.cloud.client.key") final String temporalCloudClientKey,
                       final Boolean temporalCloudEnabled,
                       @Property(name = "temporal.cloud.host") final String temporalCloudHost,
                       @Property(name = "temporal.cloud.namespace") final String temporalCloudNamespace,
                       @Property(name = "temporal.host") final String temporalHost,
                       @Property(name = "temporal.retention") final Integer temporalRetentionInDays) {
    this.activityNumberOfAttempts = activityNumberOfAttempts;
    this.initialDelayBetweenActivityAttemptsSeconds = initialDelayBetweenActivityAttemptsSeconds;
    this.maxDelayBetweenActivityAttemptsSeconds = maxDelayBetweenActivityAttemptsSeconds;
    this.temporalCloudClientCert = temporalCloudClientCert;
    this.temporalCloudClientKey = temporalCloudClientKey;
    this.temporalCloudEnabled = temporalCloudEnabled;
    this.temporalCloudHost = temporalCloudHost;
    this.temporalCloudNamespace = temporalCloudNamespace;
    this.temporalHost = temporalHost;
    this.temporalRetentionInDays = temporalRetentionInDays;
  }

  public WorkflowServiceStubs createTemporalService(final WorkflowServiceStubsOptions options, final String namespace) {
    return getTemporalClientWhenConnected(
        WAIT_INTERVAL,
        MAX_TIME_TO_CONNECT,
        WAIT_TIME_AFTER_CONNECT,
        () -> WorkflowServiceStubs.newInstance(options),
        namespace);
  }

  // TODO consider consolidating this method's logic into createTemporalService() after the Temporal
  // Cloud migration is complete.
  // The Temporal Migration migrator is the only reason this public method exists.
  public WorkflowServiceStubs createTemporalService(final boolean isCloud) {
    final WorkflowServiceStubsOptions options = isCloud ? getCloudTemporalOptions() : TemporalWorkflowUtils.getAirbyteTemporalOptions(temporalHost);
    final String namespace = isCloud ? temporalCloudNamespace : DEFAULT_NAMESPACE;

    return createTemporalService(options, namespace);
  }

  public WorkflowServiceStubs createTemporalService() {
    return createTemporalService(temporalCloudEnabled);
  }

  private WorkflowServiceStubsOptions getCloudTemporalOptions() {
    final InputStream clientCert = new ByteArrayInputStream(temporalCloudClientCert.getBytes(StandardCharsets.UTF_8));
    final InputStream clientKey = new ByteArrayInputStream(temporalCloudClientKey.getBytes(StandardCharsets.UTF_8));
    final WorkflowServiceStubsOptions.Builder optionBuilder;
    try {
      optionBuilder = WorkflowServiceStubsOptions.newBuilder()
          .setSslContext(SimpleSslContextBuilder.forPKCS8(clientCert, clientKey).build())
          .setTarget(temporalCloudHost);
    } catch (final SSLException e) {
      log.error("SSL Exception occurred attempting to establish Temporal Cloud options.");
      throw new RuntimeException(e);
    }

    configureTemporalMeterRegistry(optionBuilder);
    return optionBuilder.build();
  }

  private void configureTemporalMeterRegistry(final WorkflowServiceStubsOptions.Builder optionalBuilder) {
    final MeterRegistry registry = MetricClientFactory.getMeterRegistry();
    if (registry != null) {
      final StatsReporter reporter = new MicrometerClientStatsReporter(registry);
      final Scope scope = new RootScopeBuilder()
          .reporter(reporter)
          .reportEvery(com.uber.m3.util.Duration.ofSeconds(REPORT_INTERVAL_SECONDS));
      optionalBuilder.setMetricsScope(scope);
    }
  }

  public String getNamespace() {
    return temporalCloudEnabled ? temporalCloudNamespace : DEFAULT_NAMESPACE;
  }

  /**
   * Modifies the retention period for on-premise deployment of Temporal at the default namespace.
   * This should not be called when using Temporal Cloud, because Temporal Cloud does not allow
   * programmatic modification of workflow execution retention TTL.
   */
  public void configureTemporalNamespace(final WorkflowServiceStubs temporalService) {
    if (temporalCloudEnabled) {
      log.info("Skipping Temporal Namespace configuration because Temporal Cloud is in use.");
      return;
    }

    final var client = temporalService.blockingStub();
    final var describeNamespaceRequest = DescribeNamespaceRequest.newBuilder().setNamespace(DEFAULT_NAMESPACE).build();
    final var currentRetentionGrpcDuration = client.describeNamespace(describeNamespaceRequest).getConfig().getWorkflowExecutionRetentionTtl();
    final var currentRetention = Duration.ofSeconds(currentRetentionGrpcDuration.getSeconds());
    final var workflowExecutionTtl = Duration.ofDays(temporalRetentionInDays);
    final var humanReadableWorkflowExecutionTtl = DurationFormatUtils.formatDurationWords(workflowExecutionTtl.toMillis(), true, true);

    if (currentRetention.equals(workflowExecutionTtl)) {
      log.info("Workflow execution TTL already set for namespace " + DEFAULT_NAMESPACE + ". Remains unchanged as: "
          + humanReadableWorkflowExecutionTtl);
    } else {
      final var newGrpcDuration = com.google.protobuf.Duration.newBuilder().setSeconds(workflowExecutionTtl.getSeconds()).build();
      final var humanReadableCurrentRetention = DurationFormatUtils.formatDurationWords(currentRetention.toMillis(), true, true);
      final var namespaceConfig = NamespaceConfig.newBuilder().setWorkflowExecutionRetentionTtl(newGrpcDuration).build();
      final var updateNamespaceRequest = UpdateNamespaceRequest.newBuilder().setNamespace(DEFAULT_NAMESPACE).setConfig(namespaceConfig).build();
      log.info("Workflow execution TTL differs for namespace " + DEFAULT_NAMESPACE + ". Changing from (" + humanReadableCurrentRetention + ") to ("
          + humanReadableWorkflowExecutionTtl + "). ");
      client.updateNamespace(updateNamespaceRequest);
    }
  }

  @FunctionalInterface
  public interface TemporalJobCreator<T extends Serializable> {

    UUID create(WorkflowClient workflowClient, long jobId, int attempt, T config);

  }

  /**
   * Allows running a given temporal workflow stub asynchronously. This method only works for
   * workflows that take one argument. Because of the iface that Temporal supplies, in order to handle
   * other method signatures, if we need to support them, we will need to add another helper with that
   * number of args. For a reference on how Temporal recommends to do this see their docs:
   * https://docs.temporal.io/docs/java/workflows#asynchronous-start
   *
   * @param workflowStub - workflow stub to be executed
   * @param function - function on the workflow stub to be executed
   * @param arg1 - argument to be supplied to the workflow function
   * @param outputType - class of the output type of the workflow function
   * @param <STUB> - type of the workflow stub
   * @param <A1> - type of the argument of the workflow stub
   * @param <R> - type of the return of the workflow stub
   * @return pair of the workflow execution (contains metadata on the asynchronously running job) and
   *         future that can be used to await the result of the workflow stub's function
   */
  public <STUB, A1, R> ImmutablePair<WorkflowExecution, CompletableFuture<R>> asyncExecute(final STUB workflowStub,
                                                                                           final Functions.Func1<A1, R> function,
                                                                                           final A1 arg1,
                                                                                           final Class<R> outputType) {
    final WorkflowStub untyped = WorkflowStub.fromTyped(workflowStub);
    final WorkflowExecution workflowExecution = WorkflowClient.start(function, arg1);
    final CompletableFuture<R> resultAsync = untyped.getResultAsync(outputType);
    return ImmutablePair.of(workflowExecution, resultAsync);
  }

  /**
   * Loops and waits for the Temporal service to become available and returns a client.
   * <p>
   * This function uses a supplier as input since the creation of a WorkflowServiceStubs can result in
   * connection exceptions as well.
   */
  public WorkflowServiceStubs getTemporalClientWhenConnected(
                                                             final Duration waitInterval,
                                                             final Duration maxTimeToConnect,
                                                             final Duration waitAfterConnection,
                                                             final Supplier<WorkflowServiceStubs> temporalServiceSupplier,
                                                             final String namespace) {
    log.info("Waiting for temporal server...");

    boolean temporalNamespaceInitialized = false;
    WorkflowServiceStubs temporalService = null;
    long millisWaited = 0;

    while (!temporalNamespaceInitialized) {
      if (millisWaited >= maxTimeToConnect.toMillis()) {
        throw new RuntimeException("Could not create Temporal client within max timeout!");
      }

      log.warn("Waiting for namespace {} to be initialized in temporal...", namespace);
      Exceptions.toRuntime(() -> Thread.sleep(waitInterval.toMillis()));
      millisWaited = millisWaited + waitInterval.toMillis();

      try {
        temporalService = temporalServiceSupplier.get();
        final var namespaceInfo = getNamespaceInfo(temporalService, namespace);
        temporalNamespaceInitialized = namespaceInfo.isInitialized();
      } catch (final Exception e) {
        // Ignore the exception because this likely means that the Temporal service is still initializing.
        log.warn("Ignoring exception while trying to request Temporal namespace:", e);
      }
    }

    // sometimes it takes a few additional seconds for workflow queue listening to be available
    Exceptions.toRuntime(() -> Thread.sleep(waitAfterConnection.toMillis()));

    log.info("Temporal namespace {} initialized!", namespace);

    return temporalService;
  }

  protected NamespaceInfo getNamespaceInfo(final WorkflowServiceStubs temporalService, final String namespace) {
    return temporalService.blockingStub()
        .describeNamespace(DescribeNamespaceRequest.newBuilder().setNamespace(namespace).build())
        .getNamespaceInfo();
  }

  /**
   * Runs the code within the supplier while heartbeating in the backgroud. Also makes sure to shut
   * down the heartbeat server after the fact.
   */
  public <T> T withBackgroundHeartbeat(final Callable<T> callable,
                                       final Supplier<ActivityExecutionContext> activityContext) {
    final ScheduledExecutorService scheduledExecutor = Executors.newSingleThreadScheduledExecutor();

    try {
      scheduledExecutor.scheduleAtFixedRate(
          () -> new CancellationHandler.TemporalCancellationHandler(activityContext.get()).checkAndHandleCancellation(() -> {}),
          0, SEND_HEARTBEAT_INTERVAL.toSeconds(), TimeUnit.SECONDS);

      return callable.call();
    } catch (final ActivityCompletionException e) {
      log.warn("Job either timed out or was cancelled.");
      throw new RuntimeException(e);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    } finally {
      log.info("Stopping temporal heartbeating...");
      scheduledExecutor.shutdown();
    }
  }

  public <T> T withBackgroundHeartbeat(final AtomicReference<Runnable> cancellationCallbackRef,
                                       final Callable<T> callable,
                                       final Supplier<ActivityExecutionContext> activityContext) {
    final ScheduledExecutorService scheduledExecutor = Executors.newSingleThreadScheduledExecutor();

    try {
      scheduledExecutor.scheduleAtFixedRate(() -> {
        final CancellationHandler cancellationHandler = new CancellationHandler.TemporalCancellationHandler(activityContext.get());

        cancellationHandler.checkAndHandleCancellation(() -> {
          if (cancellationCallbackRef != null) {
            final Runnable cancellationCallback = cancellationCallbackRef.get();
            if (cancellationCallback != null) {
              cancellationCallback.run();
            }
          }
        });
      }, 0, SEND_HEARTBEAT_INTERVAL.toSeconds(), TimeUnit.SECONDS);

      return callable.call();
    } catch (final ActivityCompletionException e) {
      log.warn("Job either timed out or was cancelled.");
      throw new RuntimeException(e);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    } finally {
      log.info("Stopping temporal heartbeating...");
      scheduledExecutor.shutdown();
    }
  }

  public RetryOptions getRetryOptions() {
    return RetryOptions.newBuilder()
        .setMaximumAttempts(activityNumberOfAttempts)
        .setInitialInterval(Duration.ofSeconds(initialDelayBetweenActivityAttemptsSeconds))
        .setMaximumInterval(Duration.ofSeconds(maxDelayBetweenActivityAttemptsSeconds))
        .build();
  }

}
