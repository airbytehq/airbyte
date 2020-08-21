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
import com.google.common.io.Resources;
import io.dataline.config.ConnectionImplementation;
import io.dataline.config.StandardDiscoveryOutput;
import io.dataline.workers.BaseWorkerTestCase;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.PostgreSQLContainerHelper;
import java.io.IOException;
import java.net.URL;
import java.nio.charset.Charset;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class SingerDiscoveryWorkerTest extends BaseWorkerTestCase {

  PostgreSQLContainer db;

  @BeforeAll
  public void initDb() throws SQLException {
    db = new PostgreSQLContainer();
    db.start();
    // init db schema
    Connection con =
        DriverManager.getConnection(db.getJdbcUrl(), db.getUsername(), db.getPassword());
    con.createStatement().execute("CREATE TABLE id_and_name (id integer, name VARCHAR(200));");
  }

  @Test
  public void testPostgresDiscovery() throws IOException {
    final String jobId = "1";
    String postgresCreds = PostgreSQLContainerHelper.getSingerConfigJson(db);
    final ConnectionImplementation connectionImplementation = new ConnectionImplementation();
    final Object o = new ObjectMapper().readValue(postgresCreds, Object.class);
    connectionImplementation.setConfiguration(o);

    SingerDiscoveryWorker worker = new SingerDiscoveryWorker(SingerTap.POSTGRES);

    OutputAndStatus<StandardDiscoveryOutput> run =
        worker.run(connectionImplementation, createWorkspacePath(jobId));

    assertEquals(SUCCESSFUL, run.getStatus());

    String expectedSchema = readResource("simple_postgres_schema.json");
    final ObjectMapper objectMapper = new ObjectMapper();
    final String actualSchema = objectMapper.writeValueAsString(run.getOutput().get());

    assertTrue(run.getOutput().isPresent());
    assertJsonEquals(expectedSchema, actualSchema);
  }

  @Test
  public void testCancellation() throws IOException, InterruptedException, ExecutionException {
    final String jobId = "1";
    String postgresCreds = PostgreSQLContainerHelper.getSingerConfigJson(db);

    final ConnectionImplementation connectionImplementation = new ConnectionImplementation();
    final Object o = new ObjectMapper().readValue(postgresCreds, Object.class);
    connectionImplementation.setConfiguration(o);

    SingerDiscoveryWorker worker = new SingerDiscoveryWorker(SingerTap.POSTGRES);

    ExecutorService threadPool = Executors.newFixedThreadPool(2);
    Future<?> workerWasCancelled =
        threadPool.submit(
            () -> {
              OutputAndStatus<StandardDiscoveryOutput> output =
                  worker.run(connectionImplementation, createWorkspacePath(jobId));
              assertEquals(FAILED, output.getStatus());
            });

    TimeUnit.MILLISECONDS.sleep(50);
    worker.cancel();
    workerWasCancelled.get();
  }

  private String readResource(String name) {
    URL resource = Resources.getResource(name);
    try {
      return Resources.toString(resource, Charset.defaultCharset());
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private void assertJsonEquals(String s1, String s2) throws IOException {
    ObjectMapper mapper = new ObjectMapper();
    assertEquals(mapper.readTree(s1), mapper.readTree(s2));
  }
}
