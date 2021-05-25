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

import io.fabric8.kubernetes.api.model.ContainerBuilder;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.api.model.PodBuilder;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

public class KubePodProcessTest {

  private static final KubernetesClient CLIENT = new DefaultKubernetesClient();
  private static final String ENTRYPOINT = "/tmp/run.sh";
  private static final String TEST_IMAGE_NAME = "np_dest:dev";

  @BeforeAll
  public static void setup() {
    // TODO(Davin): Why does building the container ahead doesn't work?
    // new GenericContainer(
    // new ImageFromDockerfile(TEST_IMAGE_NAME, false)
    // .withDockerfileFromBuilder(builder -> {
    // builder
    // .from("debian")
    // .env(Map.of("AIRBYTE_ENTRYPOINT", ENTRYPOINT))
    // .entryPoint(ENTRYPOINT)
    // .build();})).withEnv("AIRBYTE_ENTRYPOINT", ENTRYPOINT);
  }

  @Nested
  class GetCommand {

    @Test
    @DisplayName("Should error if image does not have the right env var set.")
    public void testGetCommandFromImageNoCommand() {
      assertThrows(RuntimeException.class, () -> KubePodProcess.getCommandFromImage(CLIENT, "debian"));
    }

    @Test
    @DisplayName("Should error if image does not exists.")
    public void testGetCommandFromImageMissingImage() {
      assertThrows(RuntimeException.class, () -> KubePodProcess.getCommandFromImage(CLIENT, "bad_missing_image"));
    }

    @Test
    @DisplayName("Should retrieve the right command if image has the right env var set.")
    public void testGetCommandFromImageCommandPresent() throws IOException, InterruptedException {
      var command = KubePodProcess.getCommandFromImage(CLIENT, TEST_IMAGE_NAME);
      assertEquals(ENTRYPOINT, command);
    }

  }

  @Nested
  class GetPodIp {

    @Test
    @DisplayName("Should error when the given pod does not exists.")
    public void testGetPodIpNoPod() {
      assertThrows(RuntimeException.class, () -> KubePodProcess.getPodIP(CLIENT, "pod-does-not-exist"));
    }

    @Test
    @DisplayName("Should return the correct pod ip.")
    public void testGetPodIpGoodPod() throws InterruptedException {
      final String suffix = RandomStringUtils.randomAlphabetic(5).toLowerCase();
      var sleep = new ContainerBuilder()
          .withImage("busybox")
          .withName("sleep")
          .withCommand("sleep", "100000")
          .build();

      var podName = "test-get-pod-good-pod-" + suffix;
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

      Pod pod = CLIENT.pods().inNamespace("default").createOrReplace(podDef);
      CLIENT.resource(pod).waitUntilReady(20, TimeUnit.SECONDS);

      var ip = KubePodProcess.getPodIP(CLIENT, podName);
      var exp = CLIENT.pods().inNamespace("default").withName(podName).get().getStatus().getPodIP();
      assertEquals(exp, ip);
      CLIENT.resource(podDef).inNamespace("default").delete();
    }

  }

}
