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
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.dataline.commons.io.IOs;
import io.dataline.commons.json.Jsons;
import io.dataline.commons.resources.MoreResources;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class SingerDiscoverSchemaWorkerTest {

  private static final String IMAGE_NAME = "selfie:latest";
  private static final JsonNode CREDS = Jsons.jsonNode(ImmutableMap.builder().put("apiKey", "123").build());

  private Path jobRoot;
  private ProcessBuilderFactory pbf;
  private ProcessBuilder processBuilder;
  private Process process;
  private StandardDiscoverSchemaInput input;

  @BeforeEach
  public void setup() throws IOException, InterruptedException {
    jobRoot = Files.createTempDirectory("");
    pbf = mock(ProcessBuilderFactory.class);
    processBuilder = mock(ProcessBuilder.class);
    process = mock(Process.class);

    input = new StandardDiscoverSchemaInput();
    input.withConnectionConfiguration(CREDS);

    when(pbf.create(jobRoot, IMAGE_NAME, "--config", SingerDiscoverSchemaWorker.CONFIG_JSON_FILENAME, "--discover")).thenReturn(processBuilder);
    when(processBuilder.redirectError(jobRoot.resolve(SingerDiscoverSchemaWorker.ERROR_LOG_FILENAME).toFile())).thenReturn(processBuilder);
    when(processBuilder.redirectOutput(jobRoot.resolve(SingerDiscoverSchemaWorker.CATALOG_JSON_FILENAME).toFile())).thenReturn(processBuilder);
    when(processBuilder.start()).thenReturn(process);
    when(process.waitFor(1, TimeUnit.MINUTES)).thenReturn(true);

    // this would be written by the docker process.
    IOs.writeFile(jobRoot, "catalog.json", MoreResources.readResource("simple_postgres_singer_catalog.json"));
  }

  @Test
  public void testDiscoverSchema() throws IOException, InterruptedException, InvalidCredentialsException {
    SingerDiscoverSchemaWorker worker = new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf);
    OutputAndStatus<StandardDiscoverSchemaOutput> run = worker.run(input, jobRoot);

    assertEquals(JobStatus.SUCCESSFUL, run.getStatus());

    final StandardDiscoverSchemaOutput expectedOutput =
        Jsons.deserialize(MoreResources.readResource("simple_discovered_postgres_schema.json"), StandardDiscoverSchemaOutput.class);
    final StandardDiscoverSchemaOutput actualOutput = run.getOutput().get();

    assertTrue(run.getOutput().isPresent());
    assertEquals(expectedOutput, actualOutput);

    assertTrue(Files.exists(jobRoot.resolve(SingerDiscoverSchemaWorker.CONFIG_JSON_FILENAME)));
    assertTrue(Files.exists(jobRoot.resolve(SingerDiscoverSchemaWorker.CATALOG_JSON_FILENAME)));

    final JsonNode expectedConfig = Jsons.jsonNode(input.getConnectionConfiguration());
    final JsonNode actualConfig = Jsons.deserialize(IOs.readFile(jobRoot, SingerDiscoverSchemaWorker.CONFIG_JSON_FILENAME));
    assertEquals(expectedConfig, actualConfig);

    verify(pbf).create(jobRoot, IMAGE_NAME, "--config", SingerDiscoverSchemaWorker.CONFIG_JSON_FILENAME, "--discover");
    verify(processBuilder).redirectError(jobRoot.resolve(SingerDiscoverSchemaWorker.ERROR_LOG_FILENAME).toFile());
    verify(processBuilder).redirectOutput(jobRoot.resolve(SingerDiscoverSchemaWorker.CATALOG_JSON_FILENAME).toFile());
    verify(processBuilder).start();
    verify(process).waitFor(1, TimeUnit.MINUTES);
  }

  @Test
  public void testCancel() throws InvalidCredentialsException {
    SingerDiscoverSchemaWorker worker = new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf);
    worker.run(input, jobRoot);

    worker.cancel();

    verify(process).destroy();
  }

}
