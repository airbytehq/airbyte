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

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.google.common.base.Joiner;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.workers.WorkerException;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.api.model.PodBuilder;
import io.fabric8.kubernetes.api.model.PodList;
import io.fabric8.kubernetes.api.model.PodSpec;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.ApiException;
import io.kubernetes.client.openapi.Configuration;
import io.kubernetes.client.openapi.apis.CoreV1Api;
import io.kubernetes.client.openapi.models.V1Pod;
import io.kubernetes.client.openapi.models.V1PodList;
import io.kubernetes.client.util.Config;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.URL;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KubeProcessBuilderFactory implements ProcessBuilderFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeProcessBuilderFactory.class);

  private static final Path WORKSPACE_MOUNT_DESTINATION = Path.of("/workspace");

  private final Path workspaceRoot;

  public KubeProcessBuilderFactory(Path workspaceRoot) {
    this.workspaceRoot = workspaceRoot;
  }

  @Override
  public ProcessBuilder create(String jobId, int attempt, final Path jobRoot, final String imageName, final String entrypoint, final String... args)
      throws WorkerException {

    try {
      final String template = MoreResources.readResource("kube_runner_template.yaml");

      // used to differentiate source and destination processes with the same id and attempt
      final String suffix = RandomStringUtils.randomAlphabetic(5).toLowerCase();

      ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory());

      final String rendered = template.replaceAll("JOBID", jobId)
          .replaceAll("ATTEMPTID", String.valueOf(attempt))
          .replaceAll("IMAGE", imageName)
          .replaceAll("SUFFIX", suffix)
          .replaceAll("ARGS", Jsons.serialize(Arrays.asList(args)))
          .replaceAll("WORKDIR", jobRoot.toString());

      final JsonNode node = yamlMapper.readTree(rendered);
      final String overrides = Jsons.serialize(node);

      final String podName = "airbyte-worker-" + jobId + "-" + attempt + "-" + suffix;

      final List<String> cmd =
          Lists.newArrayList(
              "kubectl",
              "run",
              "--generator=run-pod/v1",
              "--rm",
              "-i",
              "--pod-running-timeout=24h",
              "--image=" + imageName,
              "--restart=Never",
              "--overrides=" + overrides, // fails if you add quotes around the overrides string
              podName);
      // TODO handle entrypoint override (to run DbtTransformationRunner for example)
      LOGGER.debug("Preparing command: {}", Joiner.on(" ").join(cmd));

      return new ProcessBuilder(cmd);
    } catch (Exception e) {
      throw new WorkerException(e.getMessage());
    }
  }

  public static void main(String[] args) throws IOException, ApiException, InterruptedException {
    // TODO: This pod sometimes errors once on start up. Why?
    var PORT = 9000;
    String IP = null;
    var destPodName = "destination-listen-and-echo";
    KubernetesClient client = new DefaultKubernetesClient();

    // Load spec and create the pod.
    var stream = KubeProcessBuilderFactory.class.getClassLoader().getResourceAsStream("destination-listen-and-echo.yaml");
    var destPodDef = client.pods().load(stream).get();
    LOGGER.info("Loaded spec: {}", destPodDef);

    var podSet = client.pods().inNamespace("default").list().getItems().stream()
        .filter(pod -> pod.getMetadata().getName().equals(destPodName)).collect(Collectors.toSet());
    if (podSet.size() == 0) {
      LOGGER.info("Pod does not exist");
      Pod destPod = client.pods().create(destPodDef);
      LOGGER.info("Created pod: {}, waiting for it to be ready", destPod);
      client.resource(destPod).waitUntilReady(1, TimeUnit.MINUTES);
      LOGGER.info("Dest Pod ready");
    }

    // TODO: Why does this not work?
    //    LOGGER.info(destPod.getStatus().getPodIP());
    //    destPod = client.resource(destPod).get();
    //    LOGGER.info("Status: {}", destPod.getStatus());
    //    LOGGER.info("IP: {}", destPod.getStatus().getPodIP());
    //    IP = destPod.getStatus().getPodIP();

    // TODO: Assign labels to pods to narrow the search.
    PodList pods = client.pods().inNamespace("default").list();
    for (Pod p : pods.getItems()) {
      LOGGER.info(p.getMetadata().getName());
      LOGGER.info(p.getStatus().getPodIP());
      // Filter by pod and retrieve IP.
      if (p.getMetadata().getName().equals(destPodName)) {
        LOGGER.info("Found IP!");
        IP = p.getStatus().getPodIP();
        break;
      }
    }

    // Send something!
    var clientSocket = new Socket(IP, PORT);
    var out = new PrintWriter(clientSocket.getOutputStream(), true);
    out.print("Hello!");
    out.close();

    client.pods().delete(destPodDef);
    // TODO: Why does this wait not work?
    client.resource(destPodDef).waitUntilCondition(pod -> !pod.getStatus().getPhase().equals("Terminating"), 1, TimeUnit.MINUTES);
    client.close();
  }

}
