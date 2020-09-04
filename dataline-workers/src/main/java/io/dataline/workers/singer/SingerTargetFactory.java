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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Charsets;
import com.google.common.collect.Streams;
import com.google.common.io.Files;
import io.dataline.commons.functional.CloseableConsumer;
import io.dataline.commons.io.IOs;
import io.dataline.commons.json.Jsons;
import io.dataline.config.StandardTargetConfig;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.DefaultSyncWorker;
import io.dataline.workers.TargetConsumer;
import io.dataline.workers.TargetFactory;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.BufferedWriter;
import java.io.OutputStreamWriter;
import java.nio.file.Path;
import org.apache.commons.io.IOUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerTargetFactory implements TargetFactory<SingerMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerTargetFactory.class);

  @VisibleForTesting
  static final String CONFIG_JSON_FILENAME = "target_config.json";

  private final String imageName;
  private final ProcessBuilderFactory pbf;

  public SingerTargetFactory(final String imageName, final ProcessBuilderFactory pbf) {
    this.imageName = imageName;
    this.pbf = pbf;
  }

  @Override
  public CloseableConsumer<SingerMessage> create(StandardTargetConfig targetConfig, Path jobRoot) {
    final JsonNode configDotJson = targetConfig.getDestinationConnectionImplementation().getConfiguration();

    // write config.json to disk
    final Path configPath = IOs.writeFile(jobRoot, CONFIG_JSON_FILENAME, Jsons.serialize(configDotJson));

    try {
      final Process targetProcess =
          pbf.create(jobRoot, imageName, "--config", configPath.toString())
              .redirectError(jobRoot.resolve(DefaultSyncWorker.TARGET_ERR_LOG).toFile())
              .start();

      // the TargetConsumer is responsible for closing this.
      BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(targetProcess.getOutputStream(), Charsets.UTF_8));
      return new TargetConsumer(writer, targetProcess);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

}
