/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import com.uber.m3.tally.RootScopeBuilder;
import com.uber.m3.tally.Scope;
import com.uber.m3.tally.StatsReporter;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.micrometer.core.instrument.MeterRegistry;
import io.micronaut.context.annotation.Property;
import io.micronaut.context.annotation.Value;
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
import jakarta.inject.Singleton;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.io.Serializable;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Duration;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;
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

  private final String temporalCloudClientCert;
  private final String temporalCloudClientKey;
  private final Boolean temporalCloudEnabled;
  private final String temporalCloudHost;
  private final String temporalCloudNamespace;
  private final String temporalHost;
  private final Integer temporalRetentionInDays;

  public TemporalUtils(@Property(name = "temporal.cloud.client.cert") final String temporalCloudClientCert,
                       @Property(name = "temporal.cloud.client.key") final String temporalCloudClientKey,
                       @Property(name = "temporal.cloud.enabled",
                                 defaultValue = "false") final Boolean temporalCloudEnabled,
                       @Value("${temporal.cloud.host}") final String temporalCloudHost,
                       @Value("${temporal.cloud.namespace}") final String temporalCloudNamespace,
                       @Value("${temporal.host}") final String temporalHost,
                       @Property(name = "${temporal.retention}",
                                 defaultValue = "30") final Integer temporalRetentionInDays) {
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

  public <T> T withBackgroundHeartbeat(final AtomicReference<Runnable> afterCancellationCallbackRef,
                                       final Callable<T> callable,
                                       final Supplier<ActivityExecutionContext> activityContext) {
    final ScheduledExecutorService scheduledExecutor = Executors.newSingleThreadScheduledExecutor();

    try {
      // Schedule the cancellation handler.
      scheduledExecutor.scheduleAtFixedRate(() -> {
        final CancellationHandler cancellationHandler = new CancellationHandler.TemporalCancellationHandler(activityContext.get());

        cancellationHandler.checkAndHandleCancellation(() -> {
          // After cancellation cleanup.
          if (afterCancellationCallbackRef != null) {
            final Runnable cancellationCallback = afterCancellationCallbackRef.get();
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

  // todo (cgardens) - there are 2 sources of truth for job path. we need to reduce this down to one,
  // once we are fully on temporal.
  public static Path getJobRoot(final Path workspaceRoot, final JobRunConfig jobRunConfig) {
    return getJobRoot(workspaceRoot, jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
  }

  public static Path getLogPath(final Path jobRoot) {
    return jobRoot.resolve(LogClientSingleton.LOG_FILENAME);
  }

  public static Path getJobRoot(final Path workspaceRoot, final String jobId, final long attemptId) {
    return getJobRoot(workspaceRoot, jobId, Math.toIntExact(attemptId));
  }

  public static Path getJobRoot(final Path workspaceRoot, final String jobId, final int attemptId) {
    return workspaceRoot
        .resolve(String.valueOf(jobId))
        .resolve(String.valueOf(attemptId));
  }

  public static void main(final String[] args) {
    final String clientKey = "-----BEGIN PRIVATE KEY-----\n"
        + "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDQPWJfRhTmKUy7\n"
        + "IEw/wVQi4xEpMxyCCAOAD6xXoqcJS/kL/U2mp/jta1ed/U75q+uwadBq1GNuGGY+\n"
        + "4ukcBjCFjYp9TVIO0NVQl4xSr2QPcCJAImKC4fBUREhuBlYINu+Tq/misGpocjTz\n"
        + "I/rmv0z6KrbIiWE5P/g6yJpx0MT8eVJtmtDIU6vJP+RtRoWb4HGN6/eoGyWUvk5q\n"
        + "fAgNMIe1uRL+j5UKvxeT4g095AIOOdBn19YQbGBoBsGkEKJPzV4pQ1zO4ZpPNcgW\n"
        + "O9FNjFWEzk5gxTuMb/H8/+KgHvU57m96u2JE+4mJxh4iZADUSLDnjVDJeH1L0hJD\n"
        + "8YTJdXzdAgMBAAECggEADlkEY6MdAoS69DOz/TqRVPwHLSsH3k+2CgdKbRlYX/Qb\n"
        + "mz9fL8noBVe9iDWxUNOPIC8SPKIYnbfRp6iTvioRAsqvTZXbvwiVggGHGhValBO6\n"
        + "UGfuGK1/lRbFVMtb9yHt3ONfBl4YXszrqAsFGQv6PkxeHrAUglDNhiNXPNtRD0Ie\n"
        + "xPGhVKf8DfNz9Mwr54gK2OEBFlpgVl5NhsvIDNSgP2SmHfJBgmMcG3iMYIR/jPdZ\n"
        + "pAi7BD3k686v3Q+N+LJShxdFCnWi0I7QDze/8qSskbeD0e7QlyxadKk9vxu6fjVi\n"
        + "XgcmG2STI60EU9zvVngZouah6gMF7P3wxnexJrpk8wKBgQD7S/SLqeLSpdp9EUdI\n"
        + "aNroODIIJCJhUjHglx+0H6O7NgVRv/NkJJssrht5I2o2BTflz2lfNYP0vD0ix/Pe\n"
        + "iPp5J/8aP6aEV+fddX7KA4nW/PA6RvKqHta4Jxjzj3D0P8NKNOk7SpZnqzmeCYa0\n"
        + "oVXTsh7AI5sEFko8bl1IMNIR7wKBgQDUIyEUxXh9aWJKdbNJWTxze+O4gKD+f69F\n"
        + "76IgW9Zh+G/kXGGoSaF+he0jiNZCqygmcS2wX1IlGrsY6DiZeA9J8+1BlSxxfKP4\n"
        + "hB5ycjLXhH1M6Sv4+swSoZAOXlnzJcXbsH0wcY4Brna61qjmwFFWiHHHWVxUNzXt\n"
        + "HLs8NDP58wKBgDZv9NDQg49oWFVhidSYylsl2UjEMyJsANwLQNXvSLPEdxCHiX03\n"
        + "JNpf+Rmb32VGah6BeO0kFarNoFzJff3GJKRcUrnn8fWXaWYjDs1KSPDmqE+nkOfj\n"
        + "eFY6OgCBIVH4AiEwJxouBTj98aRXofO9Q29xlZG/5NPU1E4VBmYeFVPHAoGBAJ5K\n"
        + "kDa1mtDJwAQbi2ph4c+yVBuqL3d3w0uGIg3POUrlXGij3mL6fjywpmBrjKU2ncEB\n"
        + "lrwShHMXXSCatxEdGxttnk3fh8gu3xNjUmzHddSHEhA/tQYV7gzA7YMrOCdMujTR\n"
        + "nrh1IydyDTohTurP+mF9cpjzvwdAI0cIt1WXBmmtAoGAbDgvT0otR0jOQ07KkGxR\n"
        + "RsXT2jHdiZ/CyqxnG1zXi/abEm/L3iAKTKIRaEWfIgR9aOypIJUDxW0GmCvGvcA0\n"
        + "mvzqFLZLoX5FkiaWLlyjL2hSRceoQAfjyybPUcMN7XdUdDPbxS4cQskDnRX84qnI\n"
        + "a3AZnVUwUxW4G9E8HGQpA7M=\n"
        + "-----END PRIVATE KEY-----";

    final String clientCert = "-----BEGIN CERTIFICATE-----\n"
        + "MIIFcjCCA1qgAwIBAgITcK+zoW/cVbkSKuQrMgEEXzr2pTANBgkqhkiG9w0BAQsF\n"
        + "ADAmMRQwEgYDVQQKEwtBaXJieXRlIEluYzEOMAwGA1UEAxMFbXktY2EwHhcNMjMw\n"
        + "MjA5MDAwODQwWhcNMjQwMjA5MDAwODM5WjAAMIIBIjANBgkqhkiG9w0BAQEFAAOC\n"
        + "AQ8AMIIBCgKCAQEA0D1iX0YU5ilMuyBMP8FUIuMRKTMcgggDgA+sV6KnCUv5C/1N\n"
        + "pqf47WtXnf1O+avrsGnQatRjbhhmPuLpHAYwhY2KfU1SDtDVUJeMUq9kD3AiQCJi\n"
        + "guHwVERIbgZWCDbvk6v5orBqaHI08yP65r9M+iq2yIlhOT/4OsiacdDE/HlSbZrQ\n"
        + "yFOryT/kbUaFm+Bxjev3qBsllL5OanwIDTCHtbkS/o+VCr8Xk+INPeQCDjnQZ9fW\n"
        + "EGxgaAbBpBCiT81eKUNczuGaTzXIFjvRTYxVhM5OYMU7jG/x/P/ioB71Oe5verti\n"
        + "RPuJicYeImQA1Eiw541QyXh9S9ISQ/GEyXV83QIDAQABo4IBvTCCAbkwDgYDVR0P\n"
        + "AQH/BAQDAgWgMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjAMBgNVHRMB\n"
        + "Af8EAjAAMB0GA1UdDgQWBBTbuVzFZ3EHiKtv2BG24iP5SZ4XwTAfBgNVHSMEGDAW\n"
        + "gBQsLrMLRDLjbOy7dzLMG4ODcbdV5TCBjQYIKwYBBQUHAQEEgYAwfjB8BggrBgEF\n"
        + "BQcwAoZwaHR0cDovL3ByaXZhdGVjYS1jb250ZW50LTYyNjljODAwLTAwMDAtMjBk\n"
        + "MS04MTdjLTE0YzE0ZWYzMDk5OC5zdG9yYWdlLmdvb2dsZWFwaXMuY29tL2IxYzVh\n"
        + "YThiM2FlYjNjNDU1MzU4L2NhLmNydDAlBgNVHREBAf8EGzAZghdoeWJyaWQtdGVz\n"
        + "dC5haXJieXRlLmNvbTCBggYDVR0fBHsweTB3oHWgc4ZxaHR0cDovL3ByaXZhdGVj\n"
        + "YS1jb250ZW50LTYyNjljODAwLTAwMDAtMjBkMS04MTdjLTE0YzE0ZWYzMDk5OC5z\n"
        + "dG9yYWdlLmdvb2dsZWFwaXMuY29tL2IxYzVhYThiM2FlYjNjNDU1MzU4L2NybC5j\n"
        + "cmwwDQYJKoZIhvcNAQELBQADggIBAIl/2DZwBiWu+JI0ghMso515hkPjBnqH2uf5\n"
        + "RErMahnDuiPh1x0icumU60T6FQyQCMXw9uZ5Zc9nvjeHSCUFnQXIDsJvAxxLNJaE\n"
        + "/0KZhFhfAnauXTKQyde0g3VA5ugdCYvCpNpBqV03r/AXi+KbjBDh90g6nJ4LeouF\n"
        + "ZEwCR/yjqLf8AvfqhjzAs5eav/lUVXTetM381jV054R7Gxu/+jBoY2cFXI/kpxtR\n"
        + "SngiXlNtf+8tk3WaP0e0NNYs4nI8BuzzPZ8UsuoRNW89jNiFNEs9mHZOFcT77SdF\n"
        + "/j5JKELzRvIe1KXefdX19KIPwCVJFIHReoJKC+hWHaO99tyT1DLLpTIaRwBI+I6F\n"
        + "WDb04qcJGmoCVVmD8irYc8esvSfT3dnhgTcWfgPyFnZXYuYKviQYcvlWp0Zd6TN2\n"
        + "fNwq1aLqMNCsMy3b9n46M3lX8UZ/PMiszVXGk3vZwyVGlK2ZhUpWww81/oAhiYQw\n"
        + "RxICnwPjDKP7+V25P0Kg5drbVmo812SLd0N7kOMKo+GaBs7WDmEUqKo/0Rl4she5\n"
        + "6FPcxZ51OEMRdH0PWI7UaiQmU1OOvVUwT15Z0XIBtplowBL22BL7klaDFoJjKCBt\n"
        + "Eram2/k3kAYAyXXJOrkZogT9X3X5Qe4BLpX6ObWXakw2Lw+vPVmKY0He54RP97N7\n"
        + "CO8jVoQ3\n"
        + "-----END CERTIFICATE-----";

    final InputStream clientCertStream = new ByteArrayInputStream(clientCert.getBytes(StandardCharsets.UTF_8));
    final InputStream clientKeyStream = new ByteArrayInputStream(clientKey.getBytes(StandardCharsets.UTF_8));
    final WorkflowServiceStubsOptions.Builder optionBuilder;
    try {
      optionBuilder = WorkflowServiceStubsOptions.newBuilder()
          .setSslContext(SimpleSslContextBuilder.forPKCS8(clientCertStream, clientKeyStream).build())
          .setTarget("hybrid-testing.ebc2e.tmprl.cloud:7233");
    } catch (final SSLException e) {
      log.error("SSL Exception occurred attempting to establish Temporal Cloud options.");
      throw new RuntimeException(e);
    }

    final WorkflowServiceStubsOptions options = optionBuilder.build();
    final String namespace = "hybrid-testing.ebc2e";



    final var service = WorkflowServiceStubs.newInstance(options);

    service.healthCheck();
  }

}
