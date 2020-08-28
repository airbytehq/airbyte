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

package io.dataline.workers;

import com.fasterxml.jackson.core.JsonProcessingException;
import io.dataline.commons.json.Jsons;
import io.dataline.db.DatabaseHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import org.apache.commons.dbcp2.BasicDataSource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class PostgreSQLContainerTestHelper {

  public static void runSqlScript(MountableFile file, PostgreSQLContainer db)
      throws IOException, InterruptedException {
    String scriptPath = "/etc/" + UUID.randomUUID().toString() + ".sql";
    db.copyFileToContainer(file, scriptPath);
    db.execInContainer(
        "psql", "-d", db.getDatabaseName(), "-U", db.getUsername(), "-a", "-f", scriptPath);
  }

  public static void wipePublicSchema(PostgreSQLContainer db) throws SQLException {
    BasicDataSource connectionPool = getConnectionPool(db);
    DatabaseHelper.execute(
        connectionPool,
        context -> {
          context.execute("DROP SCHEMA public CASCADE;");
          context.execute("CREATE SCHEMA public;");
        });
  }

  public static BasicDataSource getConnectionPool(PostgreSQLContainer db) {
    return DatabaseHelper.getConnectionPool(db.getUsername(), db.getPassword(), db.getJdbcUrl());
  }

  public static String getSingerTapConfig(PostgreSQLContainer db) throws JsonProcessingException {
    return getSingerTapConfig(
        db.getUsername(),
        db.getPassword(),
        db.getHost(),
        db.getDatabaseName(),
        String.valueOf(db.getFirstMappedPort()));
  }

  public static String getSingerTapConfig(
      String user, String password, String host, String dbname, String port) {
    Map<String, String> creds = new HashMap<>();
    creds.put("user", user);
    creds.put("password", password);
    creds.put("host", host);
    creds.put("dbname", dbname);
    creds.put("port", port);

    return Jsons.serialize(creds);
  }

  public static String getSingerTargetConfig(PostgreSQLContainer db)
      throws JsonProcessingException {
    return getSingerTargetConfig(
        db.getUsername(),
        db.getPassword(),
        db.getHost(),
        db.getDatabaseName(),
        String.valueOf(db.getFirstMappedPort()),
        "public");
  }

  // TODO this will be moved into Taps/Targets
  public static String getSingerTargetConfig(
      String user, String password, String host, String dbname, String port, String schema) {
    Map<String, String> creds = new HashMap<>();
    creds.put("postgres_username", user);
    creds.put("postgres_schema", schema);
    creds.put("postgres_password", password);
    creds.put("postgres_host", host);
    creds.put("postgres_database", dbname);
    creds.put("postgres_port", port);

    return Jsons.serialize(creds);
  }
}
