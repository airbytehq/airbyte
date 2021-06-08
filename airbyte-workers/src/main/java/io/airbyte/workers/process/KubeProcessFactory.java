/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.workers.process;

import io.airbyte.workers.WorkerException;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.BlockingQueue;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KubeProcessFactory implements ProcessFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeProcessFactory.class);

  private final String namespace;
  private final KubernetesClient kubeClient;
  private final BlockingQueue<Integer> ports;
  private final Set<Integer> claimedPorts = new HashSet<>();

  public KubeProcessFactory(String namespace, KubernetesClient kubeClient, BlockingQueue<Integer> ports) {
    this.namespace = namespace;
    this.kubeClient = kubeClient;
    this.ports = ports;
  }

  @Override
  public Process create(String jobId,
                        int attempt,
                        final Path jobRoot,
                        final String imageName,
                        final boolean usesStdin,
                        final Map<String, String> files,
                        final String entrypoint,
                        final String... args)
      throws WorkerException {
    try {
      // used to differentiate source and destination processes with the same id and attempt
      final String suffix = RandomStringUtils.randomAlphabetic(5).toLowerCase();
      final String podName = "airbyte-worker-" + jobId + "-" + attempt + "-" + suffix;

      final int stdoutLocalPort = ports.take();
      claimedPorts.add(stdoutLocalPort);
      LOGGER.info("stdoutLocalPort = " + stdoutLocalPort);

      final int stderrLocalPort = ports.take();
      claimedPorts.add(stderrLocalPort);
      LOGGER.info("stderrLocalPort = " + stderrLocalPort);

      return new KubePodProcess(
          kubeClient,
          port -> {
            if (!ports.contains(port)) {
              ports.add(port);
              LOGGER.info("Port consumer releasing: " + port);
            } else {
              LOGGER.info("Port consumer skipping releasing: " + port);
            }
          },
          podName,
          namespace,
          imageName,
          stdoutLocalPort,
          stderrLocalPort,
          usesStdin,
          files,
          entrypoint,
          args);
    } catch (Exception e) {
      throw new WorkerException(e.getMessage());
    }
  }

}
