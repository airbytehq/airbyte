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

import static io.dataline.workers.JobStatus.SUCCESSFUL;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.io.Resources;
import io.dataline.workers.BaseWorkerTestCase;
import io.dataline.workers.DiscoveryOutput;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.PostgreSQLContainerHelper;
import java.io.IOException;
import java.net.URL;
import java.nio.charset.Charset;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class SingerDiscoveryWorkerTest extends BaseWorkerTestCase {

  @Test
  public void testPostgresDiscovery() throws SQLException, IOException {
    PostgreSQLContainer db = new PostgreSQLContainer();
    db.start();
    Connection con =
        DriverManager.getConnection(db.getJdbcUrl(), db.getUsername(), db.getPassword());
    con.createStatement().execute("CREATE TABLE id_and_name (id integer, name VARCHAR(200));");

    String postgresCreds = PostgreSQLContainerHelper.getSingerConfigJson(db);
    SingerDiscoveryWorker worker =
        new SingerDiscoveryWorker(
            "1",
            postgresCreds,
            SingerTap.POSTGRES,
            getWorkspacePath().toAbsolutePath().toString(),
            "/usr/local/lib/singer/"); // TODO inject as env variable

    System.out.println(getWorkspacePath().toAbsolutePath().toString());
    System.out.println(postgresCreds);
    OutputAndStatus<DiscoveryOutput> run = worker.run();
    assertEquals(SUCCESSFUL, run.status);

    String expectedCatalog = readResource("simple_postgres_catalog.json");
    assertTrue(run.output.isPresent());
    assertJsonEquals(expectedCatalog, run.output.get().getCatalog());
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
    assertTrue(mapper.readTree(s1).equals(mapper.readTree(s2)));
  }
}
