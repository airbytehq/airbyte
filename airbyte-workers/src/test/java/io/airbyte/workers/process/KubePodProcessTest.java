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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.string.Strings;
import io.fabric8.kubernetes.api.model.ContainerBuilder;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.api.model.PodBuilder;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.io.Resources;

// Disabled until we start minikube on the node.
@Disabled
public class KubePodProcessTest {

  private static final KubernetesClient K8s = new DefaultKubernetesClient();

  private static final String ENTRYPOINT = "sh";

  private static final String TEST_IMAGE_WITH_VAR_PATH = "Dockerfile.with_var";
  private static final String TEST_IMAGE_WITH_VAR_NAME = "worker-test:with-var";

  private static final String TEST_IMAGE_NO_VAR_PATH = "Dockerfile.no_var";
  private static final String TEST_IMAGE_NO_VAR_NAME = "worker-test:no-var";

  @BeforeAll
  public static void setup() {
    var varDockerfile = Resources.getResource(TEST_IMAGE_WITH_VAR_PATH);
    DockerUtils.buildImage(varDockerfile.getPath(), TEST_IMAGE_WITH_VAR_NAME);

    var noVarDockerfile = Resources.getResource(TEST_IMAGE_NO_VAR_PATH);
    DockerUtils.buildImage(noVarDockerfile.getPath(), TEST_IMAGE_NO_VAR_NAME);
  }

  @Nested
  class GetPodIp {

    @Test
    @DisplayName("Should error when the given pod does not exists.")
    public void testGetPodIpNoPod() {
      assertThrows(RuntimeException.class, () -> KubePodProcess.getPodIP(K8s, "pod-does-not-exist", "default"));
    }

    @Test
    @DisplayName("Should return the correct pod ip.")
    public void testGetPodIpGoodPod() throws InterruptedException {
      var sleep = new ContainerBuilder()
          .withImage("busybox")
          .withName("sleep")
          .withCommand("sleep", "100000")
          .build();

      var podName = Strings.addRandomSuffix("test-get-pod-good-pod", "-", 5);
      Pod podDef = new PodBuilder()
          .withApiVersion("v1")
          .withNewMetadata()
          .withName(podName)
          .endMetadata()
          .withNewSpec()
          .withRestartPolicy("Never")
          .withRestartPolicy("Never")
          .withContainers(sleep)
          .endSpec()
          .build();

      String namespace = "default";
      Pod pod = K8s.pods().inNamespace(namespace).createOrReplace(podDef);
      K8s.resource(pod).waitUntilReady(20, TimeUnit.SECONDS);

      var ip = KubePodProcess.getPodIP(K8s, podName, namespace);
      var exp = K8s.pods().inNamespace(namespace).withName(podName).get().getStatus().getPodIP();
      assertEquals(exp, ip);
      K8s.resource(podDef).inNamespace(namespace).delete();
    }

  }

}
