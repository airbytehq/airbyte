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
import io.airbyte.commons.io.IOs;
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
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import java.util.function.Predicate;
import java.util.stream.Collectors;

import org.apache.commons.lang.StringUtils;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KubeProcessBuilderFactory implements ProcessBuilderFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeProcessBuilderFactory.class);
  private final String resourceName;

  public KubeProcessBuilderFactory() {
    this.resourceName = null; // todo: somehow make the different types of processes configurable
  }

  public KubeProcessBuilderFactory(String resourceName) {
    this.resourceName = resourceName;
  }

  @Override
  public ProcessBuilder create(String jobId, int attempt, final Path jobRoot, final String imageName, final String entrypoint, final String... args)
      throws WorkerException {

    try {
      final String template = MoreResources.readResource(resourceName);

      // used to differentiate source and destination processes with the same id and attempt
      final String suffix = RandomStringUtils.randomAlphabetic(5).toLowerCase();

      ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory());

      String command = getCommandFromImage(imageName);
      LOGGER.info("Using entrypoint from image: " + command);

      final String rendered = template.replaceAll("JOBID", jobId)
          .replaceAll("ATTEMPTID", String.valueOf(attempt))
          .replaceAll("IMAGE", imageName)
          .replaceAll("SUFFIX", suffix)
          .replaceAll("COMMAND", command)
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
//              "--rm",  todo: add this back in
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

  // todo: this should really be cached
  private static String getCommandFromImage(String imageName) throws IOException {
    final String suffix = RandomStringUtils.randomAlphabetic(5).toLowerCase();

    final String podName = "airbyte-command-fetcher-" + suffix;

    final List<String> cmd =
            Lists.newArrayList(
                    "kubectl",
                    "run",
                    "--generator=run-pod/v1",
                    "--rm",
                    "-i",
                    "--pod-running-timeout=24h",
                    "--image=" + imageName,
                    "--command=true",
                    "--restart=Never",
                    podName,
                    "--",
                    "sh",
                    "-c",
                    "echo \"AIRBYTE_ENTRYPOINT=$AIRBYTE_ENTRYPOINT\"");

    Process start = new ProcessBuilder(cmd).start();

    try(BufferedReader reader = IOs.newBufferedReader(start.getInputStream())) {
      String line;
      while ((line = reader.readLine()) != null && !line.contains("AIRBYTE_ENTRYPOINT"));

      if (line == null || !line.contains("AIRBYTE_ENTRYPOINT")) {
        throw new RuntimeException("Unable to read AIRBYTE_ENTRYPOINT from the image. Make sure this environment variable is set in the Dockerfile!");
      } else {
        String[] splits = line.split("=", 2);
        if(splits.length == 1) {
          throw new RuntimeException("Unable to read AIRBYTE_ENTRYPOINT from the image. Make sure this environment variable is set in the Dockerfile!");
        } else {
          return splits[1];
        }
      }
    }
  }

  public static void main(String[] args) {
    try {
      // todo: test this with args that are used by the process
      Process process = new KubeProcessBuilderFactory("stdout_template.yaml")
              .create(0L, 0, Path.of("/tmp"), "np_source:dev", null)
              .start();

      process.getOutputStream().write(100);
      process.getInputStream().read();

      // after running this main:
      // kubectl port-forward airbyte-worker-0-0-fmave 9000:9000
      // socat -d -d -d TCP-LISTEN:9000,bind=127.0.0.1 stdout

      LOGGER.info("waiting...");
      int code = process.waitFor();
      LOGGER.info("code = " + code);
    } catch (Exception e) {
      LOGGER.error(e.getMessage());
      e.printStackTrace();
    }
  }

}
