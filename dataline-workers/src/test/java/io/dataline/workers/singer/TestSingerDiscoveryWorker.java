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

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Maps;
import com.google.common.io.Resources;
import io.dataline.workers.BaseWorkerTestCase;
import org.testcontainers.containers.PostgreSQLContainer;

import java.io.IOException;
import java.net.URL;
import java.nio.charset.Charset;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertTrue;

public class TestSingerDiscoveryWorker extends BaseWorkerTestCase {

//  @Test
//  public void testPostgresDiscovery() throws SQLException, IOException {
//    PostgreSQLContainer db = new PostgreSQLContainer();
//    db.start();
//    Connection con =
//        DriverManager.getConnection(db.getJdbcUrl(), db.getUsername(), db.getPassword());
//    con.createStatement().execute("CREATE TABLE id_and_name (id integer, name VARCHAR(200));");
//
//    String postgresCreds = getPostgresConfigJson(db);
//    SingerDiscoveryWorker worker =
//        new SingerDiscoveryWorker(
//            "1",
//            postgresCreds,
//            SingerTap.POSTGRES,
//            getWorkspacePath().toAbsolutePath().toString(),
//            "/usr/local/lib/singer/"); // TODO inject as env variable
//
//    System.out.println(getWorkspacePath().toAbsolutePath().toString());
//    System.out.println(postgresCreds);
//    OutputAndStatus<DiscoveryOutput> run = worker.run();
//    assertEquals(SUCCESSFUL, run.status);
//
//    String expectedCatalog = readResource("simple_postgres_catalog.json");
//    assertTrue(run.output.isPresent());
//    assertJsonEquals(expectedCatalog, run.output.get().catalog);
//  }

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

  private String getPostgresConfigJson(PostgreSQLContainer psqlContainer)
      throws JsonProcessingException {
    Map<String, String> props = Maps.newHashMap();
    props.put("dbname", psqlContainer.getDatabaseName());
    props.put("filter_dbs", psqlContainer.getDatabaseName());
    props.put("user", psqlContainer.getUsername());
    props.put("password", psqlContainer.getPassword());
    props.put("host", psqlContainer.getHost());
    props.put("port", String.valueOf(psqlContainer.getFirstMappedPort()));

    return new ObjectMapper().writeValueAsString(props);
  }
}
