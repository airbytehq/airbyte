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

import com.google.common.base.Joiner;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.workers.WorkerException;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KubeProcessBuilderFactory implements ProcessBuilderFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeProcessBuilderFactory.class);

  private static final Path DATA_MOUNT_DESTINATION = Path.of("/data");
  private static final Path LOCAL_MOUNT_DESTINATION = Path.of("/local");
  private static final String IMAGE_EXISTS_SCRIPT = "image_exists.sh";

  private final String workspaceMountSource;
  private final Path workspaceRoot;
  private final String localMountSource;
  private final String networkName;
  private final Path imageExistsScriptPath;

  public KubeProcessBuilderFactory(Path workspaceRoot, String workspaceMountSource, String localMountSource, String networkName) {
    this.workspaceRoot = workspaceRoot;
    this.workspaceMountSource = workspaceMountSource;
    this.localMountSource = localMountSource;
    this.networkName = networkName;
    this.imageExistsScriptPath = prepareImageExistsScript();
  }

  private static Path prepareImageExistsScript() {
    try {
      final Path basePath = Files.createTempDirectory("scripts");
      final String scriptContents = MoreResources.readResource(IMAGE_EXISTS_SCRIPT);
      final Path scriptPath = IOs.writeFile(basePath, IMAGE_EXISTS_SCRIPT, scriptContents);
      if (!scriptPath.toFile().setExecutable(true)) {
        throw new RuntimeException(String.format("Could not set %s to executable", scriptPath));
      }
      return scriptPath;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public ProcessBuilder create(final Path jobRoot, final String imageName, final String... args) throws WorkerException {

    // todo: this check needs to exist in the script instead - it needs to be pullable by kube
    // if (!checkImageExists(imageName)) {
    // throw new WorkerException("Could not find image: " + imageName);
    // }

    try {
      final String[] split = jobRoot.toString().split("/");
      final String jobId = split[split.length - 2];
      final String attemptId = split[split.length - 1];

      final String template = MoreResources.readResource("kube_runner_template.yaml");

      final String rendered = template.replace("JOBID", jobId)
          .replace("ATTEMPTID", attemptId)
          .replace("TAGGED_IMAGE", imageName)
          .replace("WORKDIR", rebasePath(jobRoot).toString())
          .replace("ARGS", Jsons.serialize(Arrays.asList(args)));

      final String yamlPath = jobRoot.resolve("job.yaml").toAbsolutePath().toString();

      try (FileWriter writer = new FileWriter(yamlPath)) {
        writer.write(rendered);
      }

      final List<String> cmd = Lists.newArrayList("kube_runner.sh", yamlPath);

      LOGGER.debug("Preparing command: {}", Joiner.on(" ").join(cmd));

      return new ProcessBuilder(cmd);
    } catch (Exception e) {
      throw new WorkerException(e.getMessage());
    }
  }

  // todo: re-use between different process builder factories
  private Path rebasePath(final Path jobRoot) {
    final Path relativePath = workspaceRoot.relativize(jobRoot);
    return DATA_MOUNT_DESTINATION.resolve(relativePath);
  }

  // todo: re-use between different process builder factories
  // @VisibleForTesting
  // boolean checkImageExists(String imageName) {
  // try {
  // final Process process = new ProcessBuilder(imageExistsScriptPath.toString(), imageName).start();
  // LineGobbler.gobble(process.getErrorStream(), LOGGER::error);
  // LineGobbler.gobble(process.getInputStream(), LOGGER::info);
  //
  // process.waitFor(1, TimeUnit.MINUTES);
  //
  // return process.exitValue() == 0;
  //
  // } catch (IOException | InterruptedException e) {
  // throw new RuntimeException(e);
  // }
  // }

}
