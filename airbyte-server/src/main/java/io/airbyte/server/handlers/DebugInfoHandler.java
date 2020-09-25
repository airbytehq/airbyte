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

import com.google.common.collect.Lists;
import io.airbyte.api.model.DebugRead;
import io.airbyte.integrations.Integrations;
import org.apache.commons.io.IOUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static java.util.stream.Collectors.toList;

public class DebugInfoHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebugInfoHandler.class);

  public DebugRead getInfo() {
    try {
      List<Map<String, String>> integrationImages = Arrays.stream(Integrations.values())
          .map(Integrations::getTaggedImage)
          .map(image -> {
            try {
              String hash = getOutput(Lists.newArrayList("docker", "images", "--no-trunc", "--quiet", image));
              Map<String, String> result = new HashMap<>();
              result.put("hash", hash.isEmpty() ? null : hash.split(":")[1].substring(0, 12));
              result.put("image", image);
              return result;
            } catch (IOException | InterruptedException e) {
              throw new RuntimeException(e);
            }
          })
          .collect(toList());

      String runningContainers = getOutput(
          Lists.newArrayList(
              "docker",
              "ps",
              "-f",
              "name=airbyte",
              "-q"));

      List<String> outputCommand = Lists.newArrayList(
          "docker",
          "inspect",
          "--format='{{.Image}} {{.Config.Image}}'");

      outputCommand.addAll(Lists.newArrayList(runningContainers.split("\n")));

      LOGGER.error("outputCommand = " + outputCommand);

      String output = getOutput(outputCommand).replaceAll("'", "");

      LOGGER.error("output = " + output);

      List<String> coreOutput = Lists.newArrayList(output.split("\n"));

      LOGGER.error("coreOutput = " + coreOutput);

      List<Map<String, String>> coreImages = coreOutput.stream().map(x -> {
        LOGGER.error("x = " + x);

        String[] s = x.split(" ");
        String shortHash = s[0].split(":")[1].substring(0, 12);
        String taggedImage = s[1];

        return Map.of(
            "image", taggedImage,
            "hash", shortHash);
      }).collect(toList());

      // todo: split into lines
      // todo:get columns
      // todo: format into map

      // todo: list airbyte local images with docker

      DebugRead result = new DebugRead();
      result.info(Map.of(
          "images",
          Map.of("running", coreImages,
              "integrations", integrationImages)));
      return result;
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  private static String getOutput(List<String> cmd) throws IOException, InterruptedException {
    ProcessBuilder processBuilder = new ProcessBuilder(cmd);
    Process process = processBuilder.start();
    process.waitFor();

    String output = IOUtils.toString(process.getInputStream(), StandardCharsets.UTF_8);

    process.destroy();

    return output;
  }

}
