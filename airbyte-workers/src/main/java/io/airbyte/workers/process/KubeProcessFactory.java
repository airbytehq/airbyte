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

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.workers.WorkerException;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.kubernetes.client.openapi.ApiClient;
import java.nio.file.Path;
import java.util.Map;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KubeProcessFactory implements ProcessFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeProcessFactory.class);

  private final String namespace;
  private final ApiClient officialClient;
  private final KubernetesClient fabricClient;
  private final String kubeHeartbeatUrl;

  /**
   * @param namespace kubernetes namespace where spawned pods will live
   * @param officialClient official kubernetes client
   * @param fabricClient fabric8 kubernetes client
   * @param kubeHeartbeatUrl a url where if the response is not 200 the spawned process will fail
   *        itself
   * @param workerPorts a set of ports that can be used for IO socket servers
   */
  public KubeProcessFactory(String namespace,
                            ApiClient officialClient,
                            KubernetesClient fabricClient,
                            String kubeHeartbeatUrl) {
    this.namespace = namespace;
    this.officialClient = officialClient;
    this.fabricClient = fabricClient;
    this.kubeHeartbeatUrl = kubeHeartbeatUrl;
  }

  @Override
  public Process create(String jobId,
                        int attempt,
                        final Path jobRoot,
                        final String imageName,
                        final boolean usesStdin,
                        final Map<String, String> files,
                        final String entrypoint,
                        final ResourceRequirements resourceRequirements,
                        final String... args)
      throws WorkerException {
    try {
      // used to differentiate source and destination processes with the same id and attempt

      final String podName = createPodName(imageName, jobId, attempt);

      final int stdoutLocalPort = KubePortManagerSingleton.take();
      LOGGER.info("{} stdoutLocalPort = {}", podName, stdoutLocalPort);

      final int stderrLocalPort = KubePortManagerSingleton.take();
      LOGGER.info("{} stderrLocalPort = {}", podName, stderrLocalPort);

      return new KubePodProcess(
          officialClient,
          fabricClient,
          podName,
          namespace,
          imageName,
          stdoutLocalPort,
          stderrLocalPort,
          kubeHeartbeatUrl,
          usesStdin,
          files,
          entrypoint,
          resourceRequirements,
          args);
    } catch (Exception e) {
      throw new WorkerException(e.getMessage(), e);
    }
  }

  /**
   * Docker image names are by convention separated by slashes. The last portion is the image's name.
   * This is followed by a colon and a version number. e.g. airbyte/scheduler:v1 or
   * gcr.io/my-project/image-name:v2.
   *
   * Kubernetes has a maximum pod name length of 63 characters.
   *
   * With these two facts, attempt to construct a unique Pod name with the image name present for
   * easier operations.
   */
  @VisibleForTesting
  protected static String createPodName(String fullImagePath, String jobId, int attempt) {
    var versionDelimiter = ":";
    var noVersion = fullImagePath.split(versionDelimiter)[0];

    var dockerDelimiter = "/";
    var nameParts = noVersion.split(dockerDelimiter);
    var imageName = nameParts[nameParts.length - 1];

    var randSuffix = RandomStringUtils.randomAlphabetic(5).toLowerCase();
    final String suffix = "worker-" + jobId + "-" + attempt + "-" + randSuffix;

    var podName = imageName + "-" + suffix;

    var podNameLenLimit = 63;
    if (podName.length() > podNameLenLimit) {
      var extra = podName.length() - podNameLenLimit;
      imageName = imageName.substring(extra);
      podName = imageName + "-" + suffix;
    }

    return podName;
  }

}
