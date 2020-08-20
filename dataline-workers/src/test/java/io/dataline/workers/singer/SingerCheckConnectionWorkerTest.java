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

import com.fasterxml.jackson.core.JsonProcessingException;
import io.dataline.config.ConnectionImplementation;
import io.dataline.config.StandardConnectionStatus;
import io.dataline.workers.BaseWorkerTestCase;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.PostgreSQLContainerHelper;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.shaded.com.fasterxml.jackson.databind.ObjectMapper;

public class SingerCheckConnectionWorkerTest extends BaseWorkerTestCase {
  private PostgreSQLContainer db;

  @BeforeAll
  public void initDb() throws SQLException {
    db = new PostgreSQLContainer();
    db.start();
    Connection con =
        DriverManager.getConnection(db.getJdbcUrl(), db.getUsername(), db.getPassword());
    con.createStatement().execute("CREATE TABLE id_and_name (id integer, name VARCHAR(200));");
  }

  @Test
  public void testNonexistentDb()
      throws JsonProcessingException,
          org.testcontainers.shaded.com.fasterxml.jackson.core.JsonProcessingException {
    final String jobId = "1";
    String fakeDbCreds =
        PostgreSQLContainerHelper.getSingerConfigJson(
            "user", "pass", "localhost", "postgres", "111111");

    final ConnectionImplementation connectionImplementation = new ConnectionImplementation();
    final Object o = new ObjectMapper().readValue(fakeDbCreds, Object.class);
    connectionImplementation.setConfiguration(o);

    SingerCheckConnectionWorker worker = new SingerCheckConnectionWorker(SINGER_POSTGRES_TAP_PATH);
    OutputAndStatus<StandardConnectionStatus> run =
        worker.run(connectionImplementation, createWorkspacePath(jobId).toString());
    assertEquals(FAILED, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardConnectionStatus.Status.FAILURE, run.getOutput().get().getStatus());
    // TODO Once log file locations are accessible externally, also verify the correct error message
    // in the logs
  }

  @Test
  public void testIncorrectAuthCredentials()
      throws JsonProcessingException,
          org.testcontainers.shaded.com.fasterxml.jackson.core.JsonProcessingException {
    final String jobId = "1";
    String incorrectCreds =
        PostgreSQLContainerHelper.getSingerConfigJson(
            db.getUsername(),
            "wrongpassword",
            db.getHost(),
            db.getDatabaseName(),
            db.getFirstMappedPort() + "");

    SingerCheckConnectionWorker worker = new SingerCheckConnectionWorker(SINGER_POSTGRES_TAP_PATH);

    final ConnectionImplementation connectionImplementation = new ConnectionImplementation();
    final Object o = new ObjectMapper().readValue(incorrectCreds, Object.class);
    connectionImplementation.setConfiguration(o);

    OutputAndStatus<StandardConnectionStatus> run =
        worker.run(connectionImplementation, createWorkspacePath(jobId).toString());
    assertEquals(FAILED, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardConnectionStatus.Status.FAILURE, run.getOutput().get().getStatus());
    // TODO Once log file locations are accessible externally, also verify the correct error message
    // in the logs
  }

  @Test
  public void testSuccessfulConnection()
      throws JsonProcessingException,
          org.testcontainers.shaded.com.fasterxml.jackson.core.JsonProcessingException {
    final String jobId = "1";

    String creds = PostgreSQLContainerHelper.getSingerConfigJson(db);
    final ConnectionImplementation connectionImplementation = new ConnectionImplementation();
    final Object o = new ObjectMapper().readValue(creds, Object.class);
    connectionImplementation.setConfiguration(o);

    SingerCheckConnectionWorker worker = new SingerCheckConnectionWorker(SINGER_POSTGRES_TAP_PATH);
    OutputAndStatus<StandardConnectionStatus> run =
        worker.run(connectionImplementation, createWorkspacePath(jobId).toString());
    assertEquals(SUCCESSFUL, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardConnectionStatus.Status.SUCCESS, run.getOutput().get().getStatus());
    // TODO Once log file locations are accessible externally, also verify the correct error message
    // in the logs
  }
}
