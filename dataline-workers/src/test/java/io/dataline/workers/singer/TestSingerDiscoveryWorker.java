package io.dataline.workers.singer;

import static io.dataline.workers.JobStatus.SUCCESSFUL;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Maps;
import com.google.common.io.Resources;
import io.dataline.workers.BaseWorkerTestCase;
import io.dataline.workers.DiscoveryOutput;
import io.dataline.workers.OutputAndStatus;
import java.io.IOException;
import java.net.URL;
import java.nio.charset.Charset;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class TestSingerDiscoveryWorker extends BaseWorkerTestCase {

  @Test
  public void testPostgresDiscovery() throws SQLException, IOException {
    PostgreSQLContainer db = new PostgreSQLContainer();
    db.start();
    Connection con =
        DriverManager.getConnection(db.getJdbcUrl(), db.getUsername(), db.getPassword());
    con.createStatement().execute("CREATE TABLE id_and_name (id integer, name VARCHAR(200));");

    String postgresCreds = getPostgresConfigJson(db);
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
    assertJsonEquals(expectedCatalog, run.output.get().catalog);
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

  private String getPostgresConfigJson(PostgreSQLContainer psqlContainer)
      throws JsonProcessingException {
    Map<String, String> props = Maps.newHashMap();
    props.put("dbname", psqlContainer.getDatabaseName());
    props.put("user", psqlContainer.getUsername());
    props.put("password", psqlContainer.getPassword());
    props.put("host", psqlContainer.getHost());
    props.put("port", String.valueOf(psqlContainer.getFirstMappedPort()));

    return new ObjectMapper().writeValueAsString(props);
  }
}
