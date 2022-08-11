/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
class KubePodProcessTest {

  private static final KubernetesClient K8s = new DefaultKubernetesClient();

  private static final String TEST_IMAGE_WITH_VAR_PATH = "Dockerfile.with_var";
  private static final String TEST_IMAGE_WITH_VAR_NAME = "worker-test:with-var";

  private static final String TEST_IMAGE_NO_VAR_PATH = "Dockerfile.no_var";
  private static final String TEST_IMAGE_NO_VAR_NAME = "worker-test:no-var";

  @BeforeAll
  static void setup() {
    final var varDockerfile = Resources.getResource(TEST_IMAGE_WITH_VAR_PATH);
    DockerUtils.buildImage(varDockerfile.getPath(), TEST_IMAGE_WITH_VAR_NAME);

    final var noVarDockerfile = Resources.getResource(TEST_IMAGE_NO_VAR_PATH);
    DockerUtils.buildImage(noVarDockerfile.getPath(), TEST_IMAGE_NO_VAR_NAME);
  }

  @Nested
  class GetPodIp {

    @Test
    @DisplayName("Should error when the given pod does not exists.")
    void testGetPodIpNoPod() {
      assertThrows(RuntimeException.class, () -> KubePodProcess.getPodIP(K8s, "pod-does-not-exist", "default"));
    }

    @Test
    @DisplayName("Should return the correct pod ip.")
    void testGetPodIpGoodPod() throws InterruptedException {
      final var sleep = new ContainerBuilder()
          .withImage("busybox")
          .withName("sleep")
          .withCommand("sleep", "100000")
          .build();

      final var podName = Strings.addRandomSuffix("test-get-pod-good-pod", "-", 5);
      final Pod podDef = new PodBuilder()
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

      final String namespace = "default";
      final Pod pod = K8s.pods().inNamespace(namespace).createOrReplace(podDef);
      K8s.resource(pod).waitUntilReady(20, TimeUnit.SECONDS);

      final var ip = KubePodProcess.getPodIP(K8s, podName, namespace);
      final var exp = K8s.pods().inNamespace(namespace).withName(podName).get().getStatus().getPodIP();
      assertEquals(exp, ip);
      K8s.resource(podDef).inNamespace(namespace).delete();
    }

  }

}
