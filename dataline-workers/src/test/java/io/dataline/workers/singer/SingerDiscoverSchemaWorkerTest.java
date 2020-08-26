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

import static io.dataline.workers.JobStatus.FAILED;
import static io.dataline.workers.JobStatus.SUCCESSFUL;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.integrations.Integrations;
import io.dataline.workers.BaseWorkerTestCase;
import io.dataline.workers.InvalidCatalogException;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.PostgreSQLContainerTestHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class SingerDiscoverSchemaWorkerTest extends BaseWorkerTestCase {

  PostgreSQLContainer db;

  @BeforeAll
  public void initDb() throws SQLException, IOException, InterruptedException {
    db = new PostgreSQLContainer();
    db.start();
    PostgreSQLContainerTestHelper.runSqlScript(
        MountableFile.forClasspathResource("simple_postgres_init.sql"), db);
  }

  @Test
  public void testPostgresDiscovery()
      throws IOException, InvalidCredentialsException, InvalidCatalogException {
    final String jobId = "1";
    String postgresCreds = PostgreSQLContainerTestHelper.getSingerTapConfig(db);
    final Object o = new ObjectMapper().readValue(postgresCreds, Object.class);
    final StandardDiscoverSchemaInput input = new StandardDiscoverSchemaInput();
    input.setConnectionConfiguration(o);

    SingerDiscoverSchemaWorker worker =
        new SingerDiscoverSchemaWorker(Integrations.POSTGRES_TAP.getDiscoverSchemaImage());

    OutputAndStatus<StandardDiscoverSchemaOutput> run =
        worker.run(input, createWorkspacePath(jobId));

    assertEquals(SUCCESSFUL, run.getStatus());

    String expectedSchema = readResource("simple_discovered_postgres_schema.json");
    final ObjectMapper objectMapper = new ObjectMapper();
    final String actualSchema = objectMapper.writeValueAsString(run.getOutput().get());

    assertTrue(run.getOutput().isPresent());
    assertJsonEquals(expectedSchema, actualSchema);
  }

  @Test
  public void testCancellation() throws IOException, InterruptedException, ExecutionException {
    final String jobId = "1";
    String postgresCreds = PostgreSQLContainerTestHelper.getSingerTapConfig(db);

    final Object o = new ObjectMapper().readValue(postgresCreds, Object.class);

    final StandardDiscoverSchemaInput input = new StandardDiscoverSchemaInput();
    input.setConnectionConfiguration(o);

    SingerDiscoverSchemaWorker worker =
        new SingerDiscoverSchemaWorker(Integrations.POSTGRES_TAP.getDiscoverSchemaImage());

    ExecutorService threadPool = Executors.newFixedThreadPool(2);
    Future<?> workerWasCancelled =
        threadPool.submit(
            () -> {
              OutputAndStatus<StandardDiscoverSchemaOutput> output = null;
              try {
                output = worker.run(input, createWorkspacePath(jobId));
                assertEquals(FAILED, output.getStatus());
              } catch (InvalidCredentialsException e) {
                throw new RuntimeException(e);
              }
            });

    TimeUnit.MILLISECONDS.sleep(50);
    worker.cancel();
    workerWasCancelled.get();
  }
}
