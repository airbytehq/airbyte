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

import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import java.nio.file.Path;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteIntegrationLauncher implements IntegrationLauncher {

  private final static Logger LOGGER = LoggerFactory.getLogger(AirbyteIntegrationLauncher.class);

  private final String jobId;
  private final int attempt;
  private final String imageName;
  private final ProcessFactory processFactory;
  private final ResourceRequirements resourceRequirement;

  public AirbyteIntegrationLauncher(String jobId,
                                    int attempt,
                                    final String imageName,
                                    final ProcessFactory processFactory) {
    this(String.valueOf(jobId), attempt, imageName, processFactory, WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS);
  }

  public AirbyteIntegrationLauncher(String jobId,
                                    int attempt,
                                    final String imageName,
                                    final ProcessFactory processFactory,
                                    final ResourceRequirements resourceRequirement) {
    this.jobId = jobId;
    this.attempt = attempt;
    this.imageName = imageName;
    this.processFactory = processFactory;
    this.resourceRequirement = resourceRequirement;
  }

  @Override
  public Process spec(final Path jobRoot) throws WorkerException {
    return processFactory.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        false,
        Collections.emptyMap(),
        null,
        resourceRequirement,
        "spec");
  }

  @Override
  public Process check(final Path jobRoot, final String configFilename, final String configContents) throws WorkerException {
    return processFactory.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        false,
        ImmutableMap.of(configFilename, configContents),
        null,
        resourceRequirement,
        "check",
        "--config", configFilename);
  }

  @Override
  public Process discover(final Path jobRoot, final String configFilename, final String configContents) throws WorkerException {
    return processFactory.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        false,
        ImmutableMap.of(configFilename, configContents),
        null,
        resourceRequirement,
        "discover",
        "--config", configFilename);
  }

  @Override
  public Process read(final Path jobRoot,
                      final String configFilename,
                      final String configContents,
                      final String catalogFilename,
                      final String catalogContents,
                      final String stateFilename,
                      final String stateContents)
      throws WorkerException {
    final List<String> arguments = Lists.newArrayList(
        "read",
        "--config", configFilename,
        "--catalog", catalogFilename);

    final Map<String, String> files = new HashMap<>();
    files.put(configFilename, configContents);
    files.put(catalogFilename, catalogContents);

    if (stateFilename != null) {
      arguments.add("--state");
      arguments.add(stateFilename);

      Preconditions.checkNotNull(stateContents);
      files.put(stateFilename, stateContents);
    }

    return processFactory.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        false,
        files,
        null,
        resourceRequirement,
        arguments);
  }

  @Override
  public Process write(final Path jobRoot,
                       final String configFilename,
                       final String configContents,
                       final String catalogFilename,
                       final String catalogContents)
      throws WorkerException {
    final Map<String, String> files = ImmutableMap.of(
        configFilename, configContents,
        catalogFilename, catalogContents);

    return processFactory.create(
        jobId,
        attempt,
        jobRoot,
        imageName,
        true,
        files,
        null,
        resourceRequirement,
        "write",
        "--config", configFilename,
        "--catalog", catalogFilename);
  }

}
