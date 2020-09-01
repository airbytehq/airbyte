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

import com.fasterxml.jackson.databind.JsonNode;
import io.dataline.config.StandardCheckConnectionInput;
import io.dataline.config.StandardCheckConnectionOutput;
import io.dataline.integrations.Integrations;
import io.dataline.workers.BaseWorkerTestCase;
import io.dataline.workers.InvalidCatalogException;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.PostgreSQLContainerTestHelper;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

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
      throws IOException, InvalidCredentialsException, InvalidCatalogException {
    final String jobId = "1";
    JsonNode fakeDbCreds =
        PostgreSQLContainerTestHelper.getSingerTapConfig(
            "user", "pass", "localhost", "postgres", "111111");

    final StandardCheckConnectionInput standardCheckConnectionInput =
        new StandardCheckConnectionInput();
    standardCheckConnectionInput.setConnectionConfigurationJson(fakeDbCreds);

    SingerCheckConnectionWorker worker =
        new SingerCheckConnectionWorker(Integrations.POSTGRES_TAP.getCheckConnectionImage(), pbf);
    OutputAndStatus<StandardCheckConnectionOutput> run =
        worker.run(standardCheckConnectionInput, createJobRoot(jobId));

    assertEquals(FAILED, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.FAILURE, run.getOutput().get().getStatus());
    // TODO Once log file locations are accessible externally, also verify the correct error message
    // in the logs
  }

  @Test
  public void testIncorrectAuthCredentials()
      throws IOException, InvalidCredentialsException, InvalidCatalogException {
    final String jobId = "1";
    JsonNode incorrectCreds =
        PostgreSQLContainerTestHelper.getSingerTapConfig(
            db.getUsername(),
            "wrongpassword",
            db.getHost(),
            db.getDatabaseName(),
            db.getFirstMappedPort() + "");

    SingerCheckConnectionWorker worker =
        new SingerCheckConnectionWorker(Integrations.POSTGRES_TAP.getCheckConnectionImage(), pbf);

    final StandardCheckConnectionInput standardCheckConnectionInput =
        new StandardCheckConnectionInput();
    standardCheckConnectionInput.setConnectionConfigurationJson(incorrectCreds);

    OutputAndStatus<StandardCheckConnectionOutput> run =
        worker.run(standardCheckConnectionInput, createJobRoot(jobId));

    assertEquals(FAILED, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.FAILURE, run.getOutput().get().getStatus());
    // TODO Once log file locations are accessible externally, also verify the correct error message
    // in the logs
  }

  @Test
  public void testSuccessfulConnection()
      throws IOException, InvalidCredentialsException, InvalidCatalogException {
    final String jobId = "1";

    JsonNode creds = PostgreSQLContainerTestHelper.getSingerTapConfig(db);

    final StandardCheckConnectionInput standardCheckConnectionInput =
        new StandardCheckConnectionInput();
    standardCheckConnectionInput.setConnectionConfigurationJson(creds);

    SingerCheckConnectionWorker worker =
        new SingerCheckConnectionWorker(Integrations.POSTGRES_TAP.getCheckConnectionImage(), pbf);
    OutputAndStatus<StandardCheckConnectionOutput> run =
        worker.run(standardCheckConnectionInput, createJobRoot(jobId));

    assertEquals(SUCCESSFUL, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(StandardCheckConnectionOutput.Status.SUCCESS, run.getOutput().get().getStatus());
    // TODO Once log file locations are accessible externally, also verify the correct error message
    // in the logs
  }

}
