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

import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import io.airbyte.api.client.model.SourceIdRequestBody;
import io.airbyte.commons.io.IOs;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.api.model.PodBuilder;
import io.fabric8.kubernetes.api.model.Volume;
import io.fabric8.kubernetes.api.model.VolumeBuilder;
import io.fabric8.kubernetes.api.model.VolumeMount;
import io.fabric8.kubernetes.api.model.VolumeMountBuilder;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KubeProcessBuilderFactoryPOC {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeProcessBuilderFactoryPOC.class);
  public static final KubernetesClient KUBE_CLIENT = new DefaultKubernetesClient();

  public static void testSyncWorkflow() throws IOException, InterruptedException {
    LOGGER.info("Launching source process...");
    Process src = new KubePodProcess(KUBE_CLIENT, "src", "default", "np_source:dev", 9002, 9003, false, false, null, null);

    LOGGER.info("Launching destination process...");
    Process dest = new KubePodProcess(KUBE_CLIENT, "dest", "default", "np_dest:dev", 9004, 9005, true, false, null, null);

    LOGGER.info("Launching background thread to read destination lines...");
    ExecutorService executor = Executors.newSingleThreadExecutor();
    var listenTask = executor.submit(() -> {
      BufferedReader reader = new BufferedReader(new InputStreamReader(src.getErrorStream()));
      try {
        String line;
        while ((line = reader.readLine()) != null) {
          LOGGER.info("Destination sent: {}", line);
        }
      } catch (IOException e) {
        e.printStackTrace();
      }
    });

    LOGGER.info("Copying source stdout to destination stdin...");

    try (BufferedReader reader = IOs.newBufferedReader(src.getInputStream())) {
      try (PrintWriter writer = new PrintWriter(dest.getOutputStream(), true)) {
        String line;
        while ((line = reader.readLine()) != null) {
          writer.println(line);
        }
      }
    }

    LOGGER.info("Waiting for source process to terminate...");
    src.waitFor();
    LOGGER.info("Waiting for destination process to terminate...");
    dest.waitFor();

    LOGGER.info("Closing sync worker resources...");
    listenTask.cancel(true);
    executor.shutdownNow();
    // TODO(Davin, issue-3611): Figure out why these commands are not effectively shutting down OkHTTP
    // even though documentation suggests so. See
    // https://square.github.io/okhttp/4.x/okhttp/okhttp3/-ok-http-client/#shutdown-isnt-necessary
    // Instead, the pod shuts down after 5 minutes as the pool reaps the remaining idle connection after
    // 5 minutes of inactivity, as per the default configuration.
    // OK_HTTP_CLIENT.dispatcher().executorService().shutdownNow();
    // OK_HTTP_CLIENT.connectionPool().evictAll();
    // The Kube client has issues with closing the client. Since manually injecting the OkHttp client
    // also doesn't work, it is not clear whether it's OkHTTP or the Fabric client at fault.
    // See https://github.com/fabric8io/kubernetes-client/issues/2403.
    KUBE_CLIENT.close();
    LOGGER.info("Done!");
    // Manually exit for the time being.
    System.exit(0);
  }

  private static void spikeApiAndConfig() throws InterruptedException {
    Volume configVolume = new VolumeBuilder()
        .withName("airbyte-config")
        .withNewEmptyDir()
        .endEmptyDir()
        .build();

    VolumeMount pipeVolumeMount = new VolumeMountBuilder()
        .withName("airbyte-config")
        .withMountPath("/config")
        .build();

    var ip = KubePodProcess.getPodIPFuzzyMatch(KubeProcessBuilderFactoryPOC.KUBE_CLIENT, "airbyte-server", "default");
    LOGGER.info("server pod ip: {}", ip);

    var container = KubePodProcess.writeSourceConfig(ip, UUID.fromString("2e0bb52f-30bd-4f1f-8cc6-fa0382ed66b8"), "config.json", pipeVolumeMount);

    Pod pod = new PodBuilder()
        .withApiVersion("v1")
        .withNewMetadata()
        .withName("test-write-config")
        .endMetadata()
        .withNewSpec()
        .withRestartPolicy("Never")
        .withContainers(container)
        .withVolumes(configVolume)
        .endSpec()
        .build();

    LOGGER.info("Creating pod...");
    var podDefinition = KubeProcessBuilderFactoryPOC.KUBE_CLIENT.pods().inNamespace("default").createOrReplace(pod);

    LOGGER.info("Waiting until pod is ready...");
    KubeProcessBuilderFactoryPOC.KUBE_CLIENT.resource(podDefinition).waitUntilReady(5, TimeUnit.MINUTES);
  }

  public static void main(String[] args) throws InterruptedException, IOException, ApiException {
    Process checkConn = new KubePodProcess(KUBE_CLIENT,
        "check-connection",
        "default",
        "airbyte/source-postgres:dev",
        9002,
        9003,
        false,
        true,
        "config.json", UUID.fromString("f0d13643-9041-4473-ace5-f4b7f66a231a"),
        "check", "--config", "/config/config.json");

    ExecutorService executor = Executors.newSingleThreadExecutor();
    var listenTask = executor.submit(() -> {
      BufferedReader reader = new BufferedReader(new InputStreamReader(checkConn.getInputStream()));
      try {
        String line;
        while ((line = reader.readLine()) != null) {
          LOGGER.info("check connection output: {}", line);
        }
      } catch (IOException e) {
        e.printStackTrace();
      }
    });

    var listenTaskA = executor.submit(() -> {
      BufferedReader reader = new BufferedReader(new InputStreamReader(checkConn.getErrorStream()));
      try {
        String line;
        while ((line = reader.readLine()) != null) {
          LOGGER.info("check connection error: {}", line);
        }
      } catch (IOException e) {
        e.printStackTrace();
      }
    });

    LOGGER.info("Waiting for source process to terminate...");
    checkConn.waitFor();
    System.exit(0);
  }

}
