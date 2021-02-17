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

package io.airbyte.activities;

import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.DefaultGetSpecWorker;
import io.airbyte.workers.GetSpecWorker;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Random;

public class GetSpecActivityImpl implements GetSpecActivity {

  private final Path workspaceRoot;
  private final ProcessBuilderFactory pbf;

  public GetSpecActivityImpl(Path workspaceRoot, ProcessBuilderFactory pbf) {
    this.workspaceRoot = workspaceRoot;
    this.pbf = pbf;
  }

  @Override
  public ConnectorSpecification getSpec(String dockerImage) throws Exception {
    final long jobId = new Random().nextLong();
    final int attempt = 0;
    final IntegrationLauncher launcher = new AirbyteIntegrationLauncher(jobId, attempt, dockerImage, pbf);
    final Path jobRoot = workspaceRoot.resolve(String.valueOf(jobId)).resolve(String.valueOf(attempt));

    Files.createDirectories(jobRoot);

    GetSpecWorker worker = new DefaultGetSpecWorker(launcher);

    return worker.run(new JobGetSpecConfig().withDockerImage(dockerImage), jobRoot)
        .getOutput()
        .get()
        .getSpecification();
  }

}
