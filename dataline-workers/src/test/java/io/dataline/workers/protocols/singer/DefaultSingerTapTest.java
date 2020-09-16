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

package io.dataline.workers.protocols.singer;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.dataline.commons.io.IOs;
import io.dataline.commons.json.Jsons;
import io.dataline.config.Schema;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.config.StandardTapConfig;
import io.dataline.singer.SingerCatalog;
import io.dataline.singer.SingerMessage;
import io.dataline.singer.SingerStream;
import io.dataline.singer.SingerTableSchema;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.StreamFactory;
import io.dataline.workers.TestConfigHelpers;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultSingerTapTest {

  private static final String IMAGE_NAME = "hudi:latest";
  private static final String TABLE_NAME = "user_preferences";
  private static final String COLUMN_NAME = "favorite_color";

  private static final SingerCatalog SINGER_CATALOG = new SingerCatalog()
      .withStreams(Collections.singletonList(new SingerStream()
          .withStream("hudi:latest")
          .withTapStreamId("workspace")
          .withTableName(TABLE_NAME)
          .withSchema(new SingerTableSchema())));

  private static final StandardTapConfig TAP_CONFIG = WorkerUtils.syncToTapConfig(TestConfigHelpers.createSyncConfig().getValue());

  private Path jobRoot;
  private Path errorLogPath;
  private SingerDiscoverSchemaWorker discoverSchemaWorker;

  @BeforeEach
  public void setup() throws IOException {
    jobRoot = Files.createTempDirectory("test");
    errorLogPath = jobRoot.resolve(SingerSyncWorker.TAP_ERR_LOG);

    discoverSchemaWorker = mock(SingerDiscoverSchemaWorker.class);
    when(discoverSchemaWorker.run(
        new StandardDiscoverSchemaInput()
            .withConnectionConfiguration(TAP_CONFIG.getSourceConnectionImplementation().getConfiguration()),
        jobRoot.resolve(DefaultSingerTap.DISCOVERY_DIR)))
            .thenReturn(new OutputAndStatus<>(JobStatus.SUCCESSFUL, new StandardDiscoverSchemaOutput()));
    Files.writeString(
        jobRoot.resolve(DefaultSingerTap.DISCOVERY_DIR).resolve(SingerDiscoverSchemaWorker.CATALOG_JSON_FILENAME),
        Jsons.serialize(SINGER_CATALOG));
  }

  @Test
  public void test() throws Exception {
    final List<SingerMessage> expectedMessages = Lists.newArrayList(
        SingerMessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "blue"),
        SingerMessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "yellow"));
    StreamFactory streamFactory = noop -> expectedMessages.stream();

    final ProcessBuilderFactory pbf = mock(ProcessBuilderFactory.class, RETURNS_DEEP_STUBS);
    final Process process = mock(Process.class);
    final InputStream inputStream = mock(InputStream.class);

    when(pbf.create(
        jobRoot,
        IMAGE_NAME,
        "--config",
        DefaultSingerTap.CONFIG_JSON_FILENAME,
        "--properties",
        DefaultSingerTap.CATALOG_JSON_FILENAME,
        "--state",
        DefaultSingerTap.STATE_JSON_FILENAME)
        .redirectError(errorLogPath.toFile())
        .start()).thenReturn(process);
    when(process.getInputStream()).thenReturn(inputStream);

    final SingerTap tap = new DefaultSingerTap(IMAGE_NAME, pbf, streamFactory, discoverSchemaWorker);
    tap.start(TAP_CONFIG, jobRoot);

    assertEquals(
        Jsons.jsonNode(TAP_CONFIG.getSourceConnectionImplementation().getConfiguration()),
        Jsons.deserialize(IOs.readFile(jobRoot, DefaultSingerTap.CONFIG_JSON_FILENAME)));

    assertEquals(
        Jsons.jsonNode(SINGER_CATALOG),
        Jsons.deserialize(IOs.readFile(jobRoot, DefaultSingerTap.CATALOG_JSON_FILENAME)));

    assertEquals(
        Jsons.jsonNode(TAP_CONFIG.getState()),
        Jsons.deserialize(IOs.readFile(jobRoot, DefaultSingerTap.STATE_JSON_FILENAME)));

    assertEquals(expectedMessages, Lists.newArrayList(tap.attemptRead().get(), tap.attemptRead().get()));
  }

}
