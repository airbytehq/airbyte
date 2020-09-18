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
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.dataline.commons.io.IOs;
import io.dataline.commons.json.Jsons;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.config.StandardTapConfig;
import io.dataline.singer.SingerCatalog;
import io.dataline.singer.SingerMessage;
import io.dataline.singer.SingerStream;
import io.dataline.singer.SingerTableSchema;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.TestConfigHelpers;
import io.dataline.workers.WorkerConstants;
import io.dataline.workers.WorkerException;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.Assertions;
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
  private static final StandardDiscoverSchemaInput DISCOVER_SCHEMA_INPUT = new StandardDiscoverSchemaInput()
      .withConnectionConfiguration(TAP_CONFIG.getSourceConnectionImplementation().getConfiguration());

  final List<SingerMessage> MESSAGES = Lists.newArrayList(
      SingerMessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "blue"),
      SingerMessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "yellow"));

  private Path jobRoot;
  private SingerDiscoverSchemaWorker discoverSchemaWorker;
  private ProcessBuilderFactory pbf;
  private Process process;
  private SingerStreamFactory singerStreamFactory;

  @BeforeEach
  public void setup() throws IOException {
    jobRoot = Files.createTempDirectory("test");

    discoverSchemaWorker = mock(SingerDiscoverSchemaWorker.class);
    when(discoverSchemaWorker.run(
        DISCOVER_SCHEMA_INPUT,
        jobRoot.resolve(DefaultSingerTap.DISCOVERY_DIR)))
            .thenAnswer(invocation -> {
              Files.writeString(
                  jobRoot.resolve(DefaultSingerTap.DISCOVERY_DIR).resolve(WorkerConstants.CATALOG_JSON_FILENAME),
                  Jsons.serialize(SINGER_CATALOG));
              return new OutputAndStatus<>(JobStatus.SUCCESSFUL, new StandardDiscoverSchemaOutput());
            });

    pbf = mock(ProcessBuilderFactory.class, RETURNS_DEEP_STUBS);
    process = mock(Process.class, RETURNS_DEEP_STUBS);
    final InputStream inputStream = mock(InputStream.class);
    when(pbf.create(
        IMAGE_NAME,
        "--config",
        pbf.rebasePath(jobRoot.resolve(WorkerConstants.TAP_CONFIG_JSON_FILENAME)).toString(),
        "--properties",
        pbf.rebasePath(jobRoot.resolve(WorkerConstants.CATALOG_JSON_FILENAME)).toString(),
        "--state",
        pbf.rebasePath(jobRoot.resolve(WorkerConstants.INPUT_STATE_JSON_FILENAME)).toString())
        .start()).thenReturn(process);
    when(process.isAlive()).thenReturn(true);
    when(process.getInputStream()).thenReturn(inputStream);
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream("qwer".getBytes(StandardCharsets.UTF_8)));

    singerStreamFactory = noop -> MESSAGES.stream();
  }

  @Test
  public void testSuccessfulLifecycle() throws Exception {
    final SingerTap tap = new DefaultSingerTap(IMAGE_NAME, pbf, singerStreamFactory, discoverSchemaWorker);
    tap.start(TAP_CONFIG, jobRoot);

    final List<SingerMessage> messages = Lists.newArrayList();

    assertFalse(tap.isFinished());
    messages.add(tap.attemptRead().get());
    assertFalse(tap.isFinished());
    messages.add(tap.attemptRead().get());
    assertFalse(tap.isFinished());

    when(process.isAlive()).thenReturn(false);
    assertTrue(tap.isFinished());

    tap.close();

    assertEquals(
        Jsons.jsonNode(TAP_CONFIG.getSourceConnectionImplementation().getConfiguration()),
        Jsons.deserialize(IOs.readFile(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME)));
    assertEquals(
        Jsons.jsonNode(TAP_CONFIG.getState()),
        Jsons.deserialize(IOs.readFile(jobRoot, WorkerConstants.INPUT_STATE_JSON_FILENAME)));
    assertEquals(
        Jsons.jsonNode(SINGER_CATALOG),
        Jsons.deserialize(IOs.readFile(jobRoot, WorkerConstants.CATALOG_JSON_FILENAME)));

    assertEquals(MESSAGES, messages);

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).waitFor(anyLong(), any());
  }

  @Test
  public void testProcessFail() throws Exception {
    final SingerTap tap = new DefaultSingerTap(IMAGE_NAME, pbf, singerStreamFactory, discoverSchemaWorker);
    tap.start(TAP_CONFIG, jobRoot);

    when(process.exitValue()).thenReturn(1);

    Assertions.assertThrows(WorkerException.class, tap::close);
  }

  @Test
  public void testSchemaDiscoveryFail() {
    when(discoverSchemaWorker.run(any(), any())).thenReturn(new OutputAndStatus<>(JobStatus.FAILED));

    final SingerTap tap = new DefaultSingerTap(IMAGE_NAME, pbf, singerStreamFactory, discoverSchemaWorker);
    Assertions.assertThrows(WorkerException.class, () -> tap.start(TAP_CONFIG, jobRoot));

    assertFalse(Files.exists(jobRoot.resolve(WorkerConstants.TAP_CONFIG_JSON_FILENAME)));
    assertFalse(Files.exists(jobRoot.resolve(WorkerConstants.INPUT_STATE_JSON_FILENAME)));
    assertFalse(Files.exists(jobRoot.resolve(WorkerConstants.CATALOG_JSON_FILENAME)));
  }

}
