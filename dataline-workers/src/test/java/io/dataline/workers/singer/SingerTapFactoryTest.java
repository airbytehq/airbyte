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

import static org.junit.Assert.assertEquals;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.dataline.commons.io.IOs;
import io.dataline.commons.json.Jsons;
import io.dataline.config.SingerCatalog;
import io.dataline.config.SingerColumn;
import io.dataline.config.SingerColumnMap;
import io.dataline.config.SingerMessage;
import io.dataline.config.SingerStream;
import io.dataline.config.SingerTableSchema;
import io.dataline.config.SingerType;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardTapConfig;
import io.dataline.workers.DefaultSyncWorker;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.StreamFactory;
import io.dataline.workers.TestConfigHelpers;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.ProcessBuilderFactory;
import io.dataline.workers.protocol.singer.MessageUtils;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SingerTapFactoryTest {

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
    discoverSchemaJobRoot = jobRoot.resolve(SingerTapFactory.DISCOVERY_DIR);
    errorLogPath = jobRoot.resolve(DefaultSyncWorker.TAP_ERR_LOG);
  }

  @Test
  public void test() throws InvalidCredentialsException, IOException {
    StreamFactory streamFactory = mock(StreamFactory.class);
    SingerMessage recordMessage1 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "blue");
    SingerMessage recordMessage2 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "yellow");

    final List<SingerMessage> expected = Lists.newArrayList(recordMessage1, recordMessage2);

    final StandardTapConfig tapConfig =
        WorkerUtils.syncToTapConfig(TestConfigHelpers.createSyncConfig().getValue());
    StandardDiscoverSchemaInput discoverSchemaInput = new StandardDiscoverSchemaInput();
    discoverSchemaInput.setConnectionConfiguration(
        tapConfig.getSourceConnectionImplementation().getConfiguration());
    ProcessBuilderFactory pbf = mock(ProcessBuilderFactory.class);
    ProcessBuilder processBuilder = mock(ProcessBuilder.class);
    Process process = mock(Process.class);
    InputStream inputStream = mock(InputStream.class);
    SingerDiscoverSchemaWorker discoverSchemaWorker = mock(SingerDiscoverSchemaWorker.class);

    final SingerColumn singerColumn = new SingerColumn();
    singerColumn.setType(Lists.newArrayList(SingerType.NULL, SingerType.STRING));

    final SingerColumnMap singerColumnMap = new SingerColumnMap();
    singerColumnMap.setAdditionalProperty(COLUMN_NAME, singerColumn);

    final SingerTableSchema singerSchema = new SingerTableSchema();
    singerSchema.setType("object");
    singerSchema.setProperties(singerColumnMap);

    SingerStream singerStream = new SingerStream();
    singerStream.setStream(TABLE_NAME);
    singerStream.setTapStreamId(TABLE_NAME);
    singerStream.setTableName(TABLE_NAME);
    singerStream.setSchema(singerSchema);

    final SingerCatalog singerCatalog = new SingerCatalog();
    singerCatalog.setStreams(Collections.singletonList(singerStream));

    final OutputAndStatus<SingerCatalog> discoverSchemaOutput =
        new OutputAndStatus<>(JobStatus.SUCCESSFUL, singerCatalog);

    when(discoverSchemaWorker.runInternal(discoverSchemaInput, discoverSchemaJobRoot))
        .thenReturn(discoverSchemaOutput);

    when(pbf.create(
        jobRoot,
        IMAGE_NAME,
        "--config",
        SingerTapFactory.CONFIG_JSON_FILENAME,
        "--properties",
        SingerTapFactory.CATALOG_JSON_FILENAME,
        "--state",
        SingerTapFactory.STATE_JSON_FILENAME))
            .thenReturn(processBuilder);
    when(processBuilder.redirectError(errorLogPath.toFile())).thenReturn(processBuilder);
    when(processBuilder.start()).thenReturn(process);
    when(process.getInputStream()).thenReturn(inputStream);

    when(streamFactory.create(any())).thenReturn(expected.stream());

    final SingerTapFactory tapFactory =
        new SingerTapFactory(IMAGE_NAME, pbf, streamFactory, discoverSchemaWorker);
    final Stream<SingerMessage> actual = tapFactory.create(tapConfig, jobRoot);

    assertTrue(Files.exists(jobRoot));
    assertTrue(Files.exists(jobRoot.resolve(SingerTapFactory.CONFIG_JSON_FILENAME)));
    assertTrue(Files.exists(jobRoot.resolve(SingerTapFactory.CATALOG_JSON_FILENAME)));
    assertTrue(Files.exists(jobRoot.resolve(SingerTapFactory.STATE_JSON_FILENAME)));

    final JsonNode expectedConfig = Jsons.jsonNode(tapConfig.getSourceConnectionImplementation().getConfiguration());
    final JsonNode actualConfig = Jsons.deserialize(IOs.readFile(jobRoot, SingerTapFactory.CONFIG_JSON_FILENAME));
    assertEquals(expectedConfig, actualConfig);

    final JsonNode expectedCatalog = Jsons.jsonNode(singerCatalog);
    final JsonNode actualCatalog = Jsons.deserialize(IOs.readFile(jobRoot, SingerTapFactory.CATALOG_JSON_FILENAME));
    assertEquals(expectedCatalog, actualCatalog);

    final JsonNode expectedInputState = Jsons.jsonNode(tapConfig.getState());
    final JsonNode actualInputState = Jsons.deserialize(IOs.readFile(jobRoot, SingerTapFactory.STATE_JSON_FILENAME));
    assertEquals(expectedInputState, actualInputState);

    assertEquals(expected, actual.collect(Collectors.toList()));

    verify(discoverSchemaWorker).runInternal(discoverSchemaInput, discoverSchemaJobRoot);
  }

}
