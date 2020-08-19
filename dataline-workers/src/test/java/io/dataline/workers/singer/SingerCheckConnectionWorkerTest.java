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

import com.fasterxml.jackson.core.JsonProcessingException;
import io.dataline.workers.BaseWorkerTestCase;
import io.dataline.workers.CheckConnectionOutput;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.PostgreSQLContainerHelper;
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
  public void testNonexistentDb() throws JsonProcessingException {
    String fakeDbCreds =
        PostgreSQLContainerHelper.getSingerConfigJson(
            "user", "pass", "localhost", "postgres", "111111");
    SingerCheckConnectionWorker worker =
        new SingerCheckConnectionWorker(
            "1", SingerTap.POSTGRES, fakeDbCreds, getWorkspacePath().toString(), SINGER_LIB_PATH);
    OutputAndStatus<CheckConnectionOutput> output = worker.run();
    assertEquals(FAILED, output.status);
    // TODO Once log file locations are accessible externally, also verify the correct error message
    // in the logs
  }

  @Test
  public void testIncorrectAuthCredentials() throws JsonProcessingException {
    String incorrectCreds =
        PostgreSQLContainerHelper.getSingerConfigJson(
            db.getUsername(),
            "wrongpassword",
            db.getHost(),
            db.getDatabaseName(),
            db.getFirstMappedPort() + "");

    SingerCheckConnectionWorker worker =
        new SingerCheckConnectionWorker(
            "1",
            SingerTap.POSTGRES,
            incorrectCreds,
            getWorkspacePath().toString(),
            SINGER_LIB_PATH);
    OutputAndStatus<CheckConnectionOutput> run = worker.run();
    assertEquals(FAILED, run.status);
    // TODO Once log file locations are accessible externally, also verify the correct error message
    // in the logs
  }

  @Test
  public void testSuccessfulConnection() throws JsonProcessingException {
    String creds = PostgreSQLContainerHelper.getSingerConfigJson(db);

    SingerCheckConnectionWorker worker =
        new SingerCheckConnectionWorker(
            "1", SingerTap.POSTGRES, creds, getWorkspacePath().toString(), SINGER_LIB_PATH);
    OutputAndStatus<CheckConnectionOutput> run = worker.run();
    assertEquals(SUCCESSFUL, run.status);
    // TODO Once log file locations are accessible externally, also verify the correct error message
    // in the logs
  }
}
