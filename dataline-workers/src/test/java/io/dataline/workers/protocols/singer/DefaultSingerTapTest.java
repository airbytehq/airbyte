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
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.dataline.commons.io.IOs;
import io.dataline.commons.json.Jsons;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardTapConfig;
import io.dataline.singer.SingerCatalog;
import io.dataline.singer.SingerColumn;
import io.dataline.singer.SingerColumnMap;
import io.dataline.singer.SingerMessage;
import io.dataline.singer.SingerStream;
import io.dataline.singer.SingerTableSchema;
import io.dataline.singer.SingerType;
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
  private static final String JOB_ROOT_PREFIX = "workspace";
  private static final String TABLE_NAME = "user_preferences";
  private static final String COLUMN_NAME = "favorite_color";

  private Path jobRoot;
  private Path discoverSchemaJobRoot;
  private Path errorLogPath;

  @BeforeEach
  public void setup() throws IOException {
    jobRoot = Files.createTempDirectory(JOB_ROOT_PREFIX);
    discoverSchemaJobRoot = jobRoot.resolve(DefaultSingerTap.DISCOVERY_DIR);
    errorLogPath = jobRoot.resolve(SingerSyncWorker.TAP_ERR_LOG);
  }

  @Test
  public void test() throws InvalidCredentialsException, IOException {
    StreamFactory streamFactory = mock(StreamFactory.class);
    SingerMessage recordMessage1 = SingerMessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "blue");
    SingerMessage recordMessage2 = SingerMessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "yellow");

    final List<SingerMessage> expected = Lists.newArrayList(recordMessage1, recordMessage2);

    final StandardTapConfig tapConfig = WorkerUtils.syncToTapConfig(TestConfigHelpers.createSyncConfig().getValue());
    final StandardDiscoverSchemaInput discoverSchemaInput = new StandardDiscoverSchemaInput()
        .withConnectionConfiguration(tapConfig.getSourceConnectionImplementation().getConfiguration());
    final ProcessBuilderFactory pbf = mock(ProcessBuilderFactory.class);
    final ProcessBuilder processBuilder = mock(ProcessBuilder.class);
    final Process process = mock(Process.class);
    final InputStream inputStream = mock(InputStream.class);
    final SingerDiscoverSchemaWorker discoverSchemaWorker = mock(SingerDiscoverSchemaWorker.class);

    final SingerColumn singerColumn = new SingerColumn()
        .withType(Lists.newArrayList(SingerType.NULL, SingerType.STRING));

    final SingerColumnMap singerColumnMap = new SingerColumnMap()
        .withAdditionalProperty(COLUMN_NAME, singerColumn);

    final SingerTableSchema singerSchema = new SingerTableSchema()
        .withType("object")
        .withProperties(singerColumnMap);

    final SingerStream singerStream = new SingerStream()
        .withStream(TABLE_NAME)
        .withTapStreamId(TABLE_NAME)
        .withTableName(TABLE_NAME)
        .withSchema(singerSchema);

    final SingerCatalog singerCatalog = new SingerCatalog()
        .withStreams(Collections.singletonList(singerStream));

    final OutputAndStatus<SingerCatalog> discoverSchemaOutput = new OutputAndStatus<>(JobStatus.SUCCESSFUL, singerCatalog);

    when(discoverSchemaWorker.runInternal(discoverSchemaInput, discoverSchemaJobRoot))
        .thenReturn(discoverSchemaOutput);

    when(pbf.create(
        jobRoot,
        IMAGE_NAME,
        "--config",
        DefaultSingerTap.CONFIG_JSON_FILENAME,
        "--properties",
        DefaultSingerTap.CATALOG_JSON_FILENAME,
        "--state",
        DefaultSingerTap.STATE_JSON_FILENAME))
            .thenReturn(processBuilder);
    when(processBuilder.redirectError(errorLogPath.toFile())).thenReturn(processBuilder);
    when(processBuilder.start()).thenReturn(process);
    when(process.getInputStream()).thenReturn(inputStream);

    when(streamFactory.create(any())).thenReturn(expected.stream());

    final SingerTap tap = new DefaultSingerTap(IMAGE_NAME, pbf, streamFactory, discoverSchemaWorker);
    tap.start(tapConfig, jobRoot);

    assertTrue(Files.exists(jobRoot));
    assertTrue(Files.exists(jobRoot.resolve(DefaultSingerTap.CONFIG_JSON_FILENAME)));
    assertTrue(Files.exists(jobRoot.resolve(DefaultSingerTap.CATALOG_JSON_FILENAME)));
    assertTrue(Files.exists(jobRoot.resolve(DefaultSingerTap.STATE_JSON_FILENAME)));

    final JsonNode expectedConfig = Jsons.jsonNode(tapConfig.getSourceConnectionImplementation().getConfiguration());
    final JsonNode actualConfig = Jsons.deserialize(IOs.readFile(jobRoot, DefaultSingerTap.CONFIG_JSON_FILENAME));
    assertEquals(expectedConfig, actualConfig);

    final JsonNode expectedCatalog = Jsons.jsonNode(singerCatalog);
    final JsonNode actualCatalog = Jsons.deserialize(IOs.readFile(jobRoot, DefaultSingerTap.CATALOG_JSON_FILENAME));
    assertEquals(expectedCatalog, actualCatalog);

    final JsonNode expectedInputState = Jsons.jsonNode(tapConfig.getState());
    final JsonNode actualInputState = Jsons.deserialize(IOs.readFile(jobRoot, DefaultSingerTap.STATE_JSON_FILENAME));
    assertEquals(expectedInputState, actualInputState);

    assertEquals(expected, Lists.newArrayList(tap.attemptRead(), tap.attemptRead()));

    verify(discoverSchemaWorker).runInternal(discoverSchemaInput, discoverSchemaJobRoot);
  }

}
