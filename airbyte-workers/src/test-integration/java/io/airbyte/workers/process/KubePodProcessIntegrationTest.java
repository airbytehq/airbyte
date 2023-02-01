/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Maps;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.exception.WorkerException;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.informers.SharedIndexInformer;
import io.micronaut.context.annotation.Value;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import java.io.IOException;
import java.net.Inet4Address;
import java.net.ServerSocket;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.RepeatedTest;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junitpioneer.jupiter.RetryingTest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * requires kube running locally to run. If using Minikube it requires MINIKUBE=true
 * <p>
 * Must have a timeout on this class because it tests child processes that may misbehave; otherwise
 * this can hang forever during failures.
 * <p>
 * Many of the tests here use the {@link RetryingTest} annotation instead of the more common
 * {@link Test} to allow multiple tries for a test to pass. This is because these tests sometimes
 * fail transiently, and we haven't been able to fix that yet.
 * <p>
 * However, in general we should prefer using {@code @Test} instead and only resort to using
 * {@code @RetryingTest} for tests that we can't get to pass reliably. New tests should thus default
 * to using {@code @Test} if possible.
 */
@Timeout(value = 6,
         unit = TimeUnit.MINUTES)
@MicronautTest
public class KubePodProcessIntegrationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubePodProcessIntegrationTest.class);

  private static final int RANDOM_FILE_LINE_LENGTH = 100;

  private static final boolean IS_MINIKUBE = Boolean.parseBoolean(Optional.ofNullable(System.getenv("IS_MINIKUBE")).orElse("false"));
  private static List<Integer> openPorts;
  @Value("${micronaut.server.port}")
  private Integer heartbeatPort;
  private String heartbeatUrl;
  private KubernetesClient fabricClient;
  private KubeProcessFactory processFactory;
  private static final ResourceRequirements DEFAULT_RESOURCE_REQUIREMENTS = new WorkerConfigs(new EnvConfigs()).getResourceRequirements();

  @BeforeAll
  public static void init() throws Exception {
    // todo: should we offer port pairs to prevent deadlock? can create test here with fewer to get this
    openPorts = new ArrayList<>(getOpenPorts(30));
    KubePortManagerSingleton.init(new HashSet<>(openPorts.subList(1, openPorts.size() - 1)));
  }

  @BeforeEach
  public void setup() throws Exception {
    heartbeatUrl = getHost() + ":" + heartbeatPort;

    fabricClient = new DefaultKubernetesClient();

    final WorkerConfigs workerConfigs = spy(new WorkerConfigs(new EnvConfigs()));
    when(workerConfigs.getEnvMap()).thenReturn(Map.of("ENV_VAR_1", "ENV_VALUE_1"));

    processFactory = new KubeProcessFactory(workerConfigs, "default", fabricClient, heartbeatUrl, getHost(), false);
  }

  @RetryingTest(3)
  public void testInitKubePortManagerSingletonTwice() throws Exception {
    /**
     * Test init KubePortManagerSingleton twice: 1. with same ports should succeed 2. with different
     * port should fail
     *
     * Every test has been init once in BeforeAll with getOpenPorts(30)
     */

    KubePortManagerSingleton originalKubePortManager = KubePortManagerSingleton.getInstance();

    // init the second time with the same ports
    KubePortManagerSingleton.init(new HashSet<>(openPorts.subList(1, openPorts.size() - 1)));
    assertEquals(originalKubePortManager, KubePortManagerSingleton.getInstance());

    // init the second time with different ports
    final List<Integer> differentOpenPorts = new ArrayList<>(getOpenPorts(32));
    Exception exception = assertThrows(RuntimeException.class, () -> {
      KubePortManagerSingleton.init(new HashSet<>(differentOpenPorts.subList(1, differentOpenPorts.size() - 1)));
    });
    assertTrue(exception.getMessage().contains("Cannot initialize twice with different ports!"));
  }

  /**
   * In the past we've had some issues with transient / stuck pods. The idea here is to run a few at
   * once, and check that they are all running in hopes of identifying regressions that introduce
   * flakiness.
   */
  @RetryingTest(3)
  public void testConcurrentRunning() throws Exception {
    final var totalJobs = 5;

    final var pool = Executors.newFixedThreadPool(totalJobs);

    final var successCount = new AtomicInteger(0);
    final var failCount = new AtomicInteger(0);

    for (int i = 0; i < totalJobs; i++) {
      pool.submit(() -> {
        try {
          final Process process = getProcess("echo hi; sleep 1; echo hi2");
          process.waitFor();

          // the pod should be dead and in a good state
          assertFalse(process.isAlive());
          assertEquals(0, process.exitValue());
          successCount.incrementAndGet();
        } catch (final Exception e) {
          e.printStackTrace();
          failCount.incrementAndGet();
        }
      });
    }

    pool.shutdown();
    pool.awaitTermination(2, TimeUnit.MINUTES);

    assertEquals(totalJobs, successCount.get());
  }

  @RetryingTest(3)
  public void testSuccessfulSpawning() throws Exception {
    // start a finite process
    final var availablePortsBefore = KubePortManagerSingleton.getInstance().getNumAvailablePorts();
    final Process process = getProcess("echo hi; sleep 1; echo hi2");
    process.waitFor();

    // the pod should be dead and in a good state
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getInstance().getNumAvailablePorts());
    assertEquals(0, process.exitValue());
  }

  @RetryingTest(3)
  public void testLongSuccessfulSpawning() throws Exception {
    // start a finite process
    final var availablePortsBefore = KubePortManagerSingleton.getInstance().getNumAvailablePorts();
    final Process process = getProcess("echo hi; sleep 10; echo hi2");
    process.waitFor();

    // the pod should be dead and in a good state
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getInstance().getNumAvailablePorts());
    assertEquals(0, process.exitValue());
  }

  @RepeatedTest(5)
  public void testPortsReintroducedIntoPoolOnlyOnce() throws Exception {
    final var availablePortsBefore = KubePortManagerSingleton.getInstance().getNumAvailablePorts();

    // run a finite process
    final Process process = getProcess("echo hi; sleep 1; echo hi2");
    process.waitFor();

    // the pod should be dead and in a good state
    assertFalse(process.isAlive());

    // run a background process to continuously consume available ports
    final var portsTaken = new ArrayList<Integer>();
    final var executor = Executors.newSingleThreadExecutor();
    final var shouldContinueTakingPorts = new AtomicBoolean(true);
    final var doneTakingPorts = new CountDownLatch(1);

    executor.submit(() -> {
      while (shouldContinueTakingPorts.get()) {
        final var portTaken = KubePortManagerSingleton.getInstance().takeImmediately();

        if (portTaken != null) {
          LOGGER.info("portTaken = " + portTaken);
          portsTaken.add(portTaken);
        }
      }

      doneTakingPorts.countDown();
    });

    // repeatedly call exitValue (and therefore the close method)
    for (int i = 0; i < 100; i++) {
      // if exitValue no longer calls close in the future this test will fail and need to be updated.
      process.exitValue();
    }

    assertEquals(0, process.exitValue());

    // wait for the background loop to actually take the ports re-offered by the closure of the process
    Thread.sleep(1000);

    // tell the thread to stop taking ports
    shouldContinueTakingPorts.set(false);

    // wait for the thread to actually stop taking ports
    assertTrue(doneTakingPorts.await(5, TimeUnit.SECONDS));

    // interrupt thread
    executor.shutdownNow();

    // prior to fixing this race condition, the close method would offer ports every time it was called.
    // without the race condition, we should have only been able to pull each of the originally
    // available ports once
    assertEquals(availablePortsBefore, portsTaken.size());

    // release ports for next tests
    portsTaken.forEach(KubePortManagerSingleton.getInstance()::offer);
  }

  @RetryingTest(3)
  public void testSuccessfulSpawningWithQuotes() throws Exception {
    // start a finite process
    final var availablePortsBefore = KubePortManagerSingleton.getInstance().getNumAvailablePorts();
    final Process process = getProcess("echo \"h\\\"i\"; sleep 1; echo hi2");
    final var output = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
    assertEquals("h\"i\nhi2\n", output);
    process.waitFor();

    // the pod should be dead and in a good state
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getInstance().getNumAvailablePorts());
    assertEquals(0, process.exitValue());
  }

  @RetryingTest(3)
  public void testEnvMapSet() throws Exception {
    // start a finite process
    final Process process = getProcess("echo ENV_VAR_1=$ENV_VAR_1");
    final var output = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
    assertEquals("ENV_VAR_1=ENV_VALUE_1\n", output);
    process.waitFor();

    // the pod should be dead and in a good state
    assertFalse(process.isAlive());
    assertEquals(0, process.exitValue());
  }

  @RetryingTest(3)
  public void testPipeInEntrypoint() throws Exception {
    // start a process that has a pipe in the entrypoint
    final var availablePortsBefore = KubePortManagerSingleton.getInstance().getNumAvailablePorts();
    final Process process = getProcess("echo hi | cat");
    process.waitFor();

    // the pod should be dead and in a good state
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getInstance().getNumAvailablePorts());
    assertEquals(0, process.exitValue());
  }

  @RetryingTest(3)
  @Timeout(20)
  public void testDeletingPodImmediatelyAfterCompletion() throws Exception {
    // start a process that requests
    final var availablePortsBefore = KubePortManagerSingleton.getInstance().getNumAvailablePorts();
    final var uuid = UUID.randomUUID();
    final Process process = getProcess(Map.of("uuid", uuid.toString()), "sleep 1 && exit 10");

    final var pod = fabricClient.pods().list().getItems().stream().filter(p -> p.getMetadata() != null && p.getMetadata().getLabels() != null)
        .filter(p -> p.getMetadata().getLabels().containsKey("uuid") && p.getMetadata().getLabels().get("uuid").equals(uuid.toString()))
        .collect(Collectors.toList()).get(0);
    final SharedIndexInformer<Pod> podInformer =
        fabricClient.pods().inNamespace(pod.getMetadata().getNamespace()).withName(pod.getMetadata().getName()).inform();
    podInformer.addEventHandler(new ExitCodeWatcher(pod.getMetadata().getName(), pod.getMetadata().getNamespace(), exitCode -> {
      fabricClient.pods().delete(pod);
    }, () -> {}));

    process.waitFor();

    // the pod should be dead with the correct error code
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getInstance().getNumAvailablePorts());
    assertEquals(10, process.exitValue());
  }

  @RetryingTest(3)
  public void testExitCodeRetrieval() throws Exception {
    // start a process that requests
    final var availablePortsBefore = KubePortManagerSingleton.getInstance().getNumAvailablePorts();
    final Process process = getProcess("exit 10");
    process.waitFor();

    // the pod should be dead with the correct error code
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getInstance().getNumAvailablePorts());
    assertEquals(10, process.exitValue());
  }

  @RetryingTest(3)
  public void testMissingEntrypoint() throws WorkerException, InterruptedException {
    // start a process with an entrypoint that doesn't exist
    final var availablePortsBefore = KubePortManagerSingleton.getInstance().getNumAvailablePorts();
    final Process process = getProcess(null);
    process.waitFor();

    // the pod should be dead and in an error state
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getInstance().getNumAvailablePorts());
    assertEquals(127, process.exitValue());
  }

  @RetryingTest(3)
  public void testKillingWithoutHeartbeat() throws Exception {
    heartbeatUrl = "invalid_host";

    fabricClient = new DefaultKubernetesClient();

    final WorkerConfigs workerConfigs = spy(new WorkerConfigs(new EnvConfigs()));
    when(workerConfigs.getEnvMap()).thenReturn(Map.of("ENV_VAR_1", "ENV_VALUE_1"));

    processFactory = new KubeProcessFactory(workerConfigs, "default", fabricClient, heartbeatUrl, getHost(), false);

    // start an infinite process
    final var availablePortsBefore = KubePortManagerSingleton.getInstance().getNumAvailablePorts();
    final Process process = getProcess("while true; do echo hi; sleep 1; done");

    // waiting for process
    process.waitFor();

    // the pod should be dead and in an error state
    assertFalse(process.isAlive());
    assertEquals(availablePortsBefore, KubePortManagerSingleton.getInstance().getNumAvailablePorts());
    assertNotEquals(0, process.exitValue());
  }

  @RetryingTest(3)
  public void testExitValueWaitsForMainToTerminate() throws Exception {
    // start a long running main process
    final Process process = getProcess("sleep 2; exit 13;");

    // immediately close streams
    process.getInputStream().close();
    process.getOutputStream().close();

    // waiting for process
    process.waitFor();

    // the pod exit code should match the main container exit value
    assertEquals(13, process.exitValue());
  }

  @RetryingTest(3)
  public void testCopyLargeFiles() throws Exception {
    final int numFiles = 1;
    final int numLinesPerFile = 200000;

    final Map<String, String> files = Maps.newHashMapWithExpectedSize(numFiles);
    for (int i = 0; i < numFiles; i++) {
      files.put("file" + i, getRandomFile(numLinesPerFile));
    }

    final long minimumConfigDirSize = (long) numFiles * numLinesPerFile * RANDOM_FILE_LINE_LENGTH;

    final Process process = getProcess(
        String.format("CONFIG_DIR_SIZE=$(du -sb /config | awk '{print $1;}'); if [ $CONFIG_DIR_SIZE -ge %s ]; then exit 10; else exit 1; fi;",
            minimumConfigDirSize),
        files);

    process.waitFor();
    assertEquals(10, process.exitValue());
  }

  private static String getRandomFile(final int lines) {
    final var sb = new StringBuilder();
    for (int i = 0; i < lines; i++) {
      sb.append(RandomStringUtils.randomAlphabetic(RANDOM_FILE_LINE_LENGTH));
      sb.append("\n");
    }
    return sb.toString();
  }

  private Process getProcess(final String entrypoint) throws WorkerException {
    // these files aren't used for anything, it's just to check for exceptions when uploading
    final var files = ImmutableMap.of("file0", "fixed str", "file1", getRandomFile(1), "file2", getRandomFile(100), "file3", getRandomFile(1000));

    return getProcess(entrypoint, files);
  }

  private Process getProcess(final Map<String, String> customLabels, final String entrypoint) throws WorkerException {
    return getProcess(customLabels, entrypoint, Map.of());
  }

  private Process getProcess(final String entrypoint, final Map<String, String> files) throws WorkerException {
    return getProcess(Map.of(), entrypoint, files);
  }

  private Process getProcess(final Map<String, String> customLabels, final String entrypoint, final Map<String, String> files)
      throws WorkerException {
    return processFactory.create("tester", "some-id", 0, Path.of("/tmp/job-root"), "busybox:latest", false, false, files, entrypoint,
        DEFAULT_RESOURCE_REQUIREMENTS, null, customLabels, Collections.emptyMap(), Collections.emptyMap());
  }

  private static Set<Integer> getOpenPorts(final int count) {
    final Set<ServerSocket> servers = new HashSet<>();
    final Set<Integer> ports = new HashSet<>();

    try {
      for (int i = 0; i < count; i++) {
        final var server = new ServerSocket(0);
        servers.add(server);
        ports.add(server.getLocalPort());
      }
    } catch (final IOException e) {
      throw new RuntimeException(e);
    } finally {
      for (final ServerSocket server : servers) {
        Exceptions.swallow(server::close);
      }
    }

    return ports;
  }

  private static String getHost() {
    try {
      return (IS_MINIKUBE ? Inet4Address.getLocalHost().getHostAddress() : "host.docker.internal");
    } catch (final UnknownHostException e) {
      throw new RuntimeException(e);
    }
  }

}
