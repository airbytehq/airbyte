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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.workers.DefaultDiscoverCatalogWorker;
import io.airbyte.workers.DiscoverCatalogWorker;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import io.temporal.activity.ActivityInfo;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Random;

public class DiscoverCatalogActivityImpl implements DiscoverCatalogActivity {

  private final Path workspaceRoot;
  private final ProcessBuilderFactory pbf;

  public DiscoverCatalogActivityImpl(Path workspaceRoot, ProcessBuilderFactory pbf) {
    this.workspaceRoot = workspaceRoot;
    this.pbf = pbf;
  }

  @Override
  public AirbyteCatalog discoverCatalog(String dockerImage, JsonNode connectionConfig) throws IOException {
    final ActivityInfo activityInfo = Activity.getExecutionContext().getInfo();
    final String jobId = activityInfo.getWorkflowId();
    final int attempt = activityInfo.getAttempt();

    final IntegrationLauncher launcher = new AirbyteIntegrationLauncher(jobId, attempt, dockerImage, pbf);
    final Path jobRoot = workspaceRoot.resolve(jobId).resolve(String.valueOf(attempt));

    Files.createDirectories(jobRoot);

    DiscoverCatalogWorker worker = new DefaultDiscoverCatalogWorker(launcher);

    return worker.run(new StandardDiscoverCatalogInput().withConnectionConfiguration(connectionConfig), jobRoot)
        .getOutput()
        .get()
        .getCatalog();
  }

}
