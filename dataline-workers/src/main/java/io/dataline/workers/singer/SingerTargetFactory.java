/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.workers.singer;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.Charsets;
import io.dataline.commons.functional.CloseableConsumer;
import io.dataline.config.SingerMessage;
import io.dataline.config.StandardTargetConfig;
import io.dataline.workers.DefaultSyncWorker;
import io.dataline.workers.TargetConsumer;
import io.dataline.workers.TargetFactory;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerTargetFactory implements TargetFactory<SingerMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerTargetFactory.class);

  private static final String CONFIG_JSON_FILENAME = "target_config.json";

  private final String imageName;
  private final ProcessBuilderFactory pbf;

  public SingerTargetFactory(final String imageName, final ProcessBuilderFactory pbf) {
    this.imageName = imageName;
    this.pbf = pbf;
  }

  @Override
  public CloseableConsumer<SingerMessage> create(StandardTargetConfig targetConfig, Path jobRoot) {
    final ObjectMapper objectMapper = new ObjectMapper();
    final String configDotJson;

    try {
      configDotJson =
          objectMapper.writeValueAsString(
              targetConfig.getDestinationConnectionImplementation().getConfiguration());
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }

    // write config.json to disk
    Path configPath =
        WorkerUtils.writeFileToWorkspace(jobRoot, CONFIG_JSON_FILENAME, configDotJson);

    try {
      final Process targetProcess =
          pbf.create(jobRoot, imageName, "--config", configPath.toString())
              .redirectError(jobRoot.resolve(DefaultSyncWorker.TARGET_ERR_LOG).toFile())
              .start();

      try (BufferedWriter writer =
          new BufferedWriter(
              new OutputStreamWriter(targetProcess.getOutputStream(), Charsets.UTF_8))) {

        return new TargetConsumer(writer, targetProcess);
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }
}
