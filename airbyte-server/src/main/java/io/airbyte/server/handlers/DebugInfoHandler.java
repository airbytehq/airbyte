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

package io.airbyte.server.handlers;

import static java.util.stream.Collectors.toList;

import com.google.common.collect.Lists;
import io.airbyte.api.model.DebugRead;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.integrations.Integrations;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Nullable;
import org.apache.commons.io.IOUtils;

public class DebugInfoHandler {

  public DebugRead getInfo() {
    List<Map<String, String>> integrationImages = getIntegrationImages();
    List<Map<String, String>> runningCoreImages = getRunningCoreImages();

    DebugRead result = new DebugRead();
    result.info(Map.of(
        "images", Map.of(
            "running", runningCoreImages,
            "integrations", integrationImages)));
    return result;
  }

  private static List<Map<String, String>> getRunningCoreImages() {
    try {
      String runningAirbyteContainers = runAndGetOutput(
          Lists.newArrayList(
              "docker",
              "ps",
              "-f",
              "name=airbyte",
              "-q"));

      List<String> inspectCommand = Lists.newArrayList(
          "docker",
          "inspect",
          "--format='{{.Image}} {{.Config.Image}}'");

      inspectCommand.addAll(Lists.newArrayList(runningAirbyteContainers.split("\n")));

      String output = runAndGetOutput(inspectCommand).replaceAll("'", "");

      List<String> coreOutput = Lists.newArrayList(output.split("\n"));

      return coreOutput.stream().map(entry -> {
        String[] elements = entry.split(" ");
        String shortHash = getShortHash(elements[0]);
        String taggedImage = elements[1];

        Map<String, String> result = new HashMap<>();
        result.put("hash", shortHash);
        result.put("image", taggedImage);
        return result;
      }).collect(toList());
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  private static List<Map<String, String>> getIntegrationImages() {
    try {
      return Arrays.stream(Integrations.values())
          .map(Integrations::getTaggedImage)
          .map(image -> {
            try {
              String hash = runAndGetOutput(Lists.newArrayList("docker", "images", "--no-trunc", "--quiet", image));
              Map<String, String> result = new HashMap<>();
              result.put("hash", getShortHash(hash));
              result.put("image", image);
              return result;
            } catch (IOException | InterruptedException e) {
              throw new RuntimeException(e);
            }
          })
          .collect(toList());
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  protected static String runAndGetOutput(List<String> cmd) throws IOException, InterruptedException {
    ProcessBuilder processBuilder = new ProcessBuilder(cmd);
    Process process = processBuilder.start();
    process.waitFor();

    String output = IOUtils.toString(process.getInputStream(), StandardCharsets.UTF_8);

    process.destroy();

    return output;
  }

  @Nullable
  protected static String getShortHash(String sha256TaggedHash) {
    if (sha256TaggedHash.isEmpty()) {
      return null;
    } else {
      String fullHash = sha256TaggedHash.replace("sha256:", "");
      return fullHash.substring(0, Math.min(12, fullHash.length()));
    }
  }

}
