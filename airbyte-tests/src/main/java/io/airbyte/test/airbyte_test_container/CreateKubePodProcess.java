package io.airbyte.test.airbyte_test_container;

import io.airbyte.commons.string.Strings;
import io.airbyte.config.EnvConfigs;
import io.airbyte.workers.process.KubePodProcess;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class CreateKubePodProcess {

  public static void main(final String[] args) throws IOException, InterruptedException {
    final var configs = new EnvConfigs();

    // first deploy a pod that is just listening
    final var processRunnerHost = "echoserver:80"; // this needs to be ip of the listener pod

    final var fabricClient = new DefaultKubernetesClient();
    final var namespace = "default";
    final var image = "alpine:3.14";
    final var stdOutLocalPort = 9001;
    final var stdErrLocalPort = 9002;
    final var heartBeatUrl = "echoserver:80";

    final var testNumPods = 50;
    for (int i = 0; i < testNumPods; i++) {
      final var podName = Strings.addRandomSuffix("test-pod", "-", 5);;
      try {
        final var process = new KubePodProcess(
            false,
            processRunnerHost,
            fabricClient,
            KubePodProcess.DEFAULT_STATUS_CHECK_INTERVAL,
            podName,
            namespace,
            image,
            "IfNotPresent",
            stdOutLocalPort,
            stdErrLocalPort,
            heartBeatUrl,
            false,
            Map.of(), // nothing to copy for now
            "sleep 1",
            new io.airbyte.config.ResourceRequirements(),
            configs.getJobKubeMainContainerImagePullSecret(),
            List.of(), // no tolerations
            Map.of(), // no node selectors
            Map.of(), // no labels
            configs.getJobKubeSocatImage(),
            configs.getJobKubeBusyboxImage(),
            configs.getJobKubeCurlImage(),
            Map.of(),
            Map.of());
        final var exit = process.waitFor();
        System.out.println(exit);
      } catch (final Exception e) {
        log.info("Error: ", e);
      }
    }

    fabricClient.close();
  }

}
