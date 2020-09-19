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
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DockerProcessBuilderFactory implements ProcessBuilderFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(DockerProcessBuilderFactory.class);

  private static final Path DATA_MOUNT_DESTINATION = Path.of("/data");
  private static final Path LOCAL_MOUNT_DESTINATION = Path.of("/local");

  private final String workspaceMountSource;
  private final Path workspaceRoot;
  private String localMountSource;
  private final String networkName;

  public DockerProcessBuilderFactory(Path workspaceRoot, String workspaceMountSource, String localMountSource, String networkName) {
    this.workspaceMountSource = workspaceMountSource;
    this.workspaceRoot = workspaceRoot;
    this.localMountSource = localMountSource;
    this.networkName = networkName;
  }

  @Override
  public ProcessBuilder create(final Path jobRoot, final String imageName, final String... args) {
    final List<String> cmd =
        Lists.newArrayList(
            "docker",
            "run",
            "--rm",
            "-i",
            "-v",
            String.format("%s:%s", workspaceMountSource, DATA_MOUNT_DESTINATION),
            "-v",
            String.format("%s:%s", localMountSource, LOCAL_MOUNT_DESTINATION),
            "-w",
            rebasePath(jobRoot).toString(),
            "--network",
            networkName,
            imageName);
    cmd.addAll(Arrays.asList(args));

    LOGGER.debug("Preparing command: {}", Joiner.on(" ").join(cmd));

    return new ProcessBuilder(cmd);
  }

  private Path rebasePath(final Path jobRoot) {
    final Path relativePath = workspaceRoot.relativize(jobRoot);
    return DATA_MOUNT_DESTINATION.resolve(relativePath);
  }

}
