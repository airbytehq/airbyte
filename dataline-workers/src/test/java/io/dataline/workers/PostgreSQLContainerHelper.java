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
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Sets;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import org.testcontainers.containers.PostgreSQLContainer;

public class PostgreSQLContainerHelper {

  public static String getSingerConfigJson(PostgreSQLContainer db) throws JsonProcessingException {
    return getSingerConfigJson(
        db.getUsername(),
        db.getPassword(),
        db.getHost(),
        db.getDatabaseName(),
        String.valueOf(db.getFirstMappedPort()));
  }

  public static String getSingerConfigJson(
      String user, String password, String host, String dbname, String port)
      throws JsonProcessingException {
    Map<String, String> creds = new HashMap<>();
    creds.put("user", user);
    creds.put("password", password);
    creds.put("host", host);
    creds.put("dbname", dbname);
    creds.put("port", port);

    return new ObjectMapper().writeValueAsString(creds);
  }

  public static Set<String> getTables(PostgreSQLContainer db) throws SQLException {
    ResultSet resultSet =
        DriverManager.getConnection(db.getJdbcUrl(), db.getUsername(), db.getPassword())
            .createStatement()
            .executeQuery(
                "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'");

    Set<String> tableNames = Sets.newHashSet();
    while (resultSet.next()) {
      tableNames.add(resultSet.getString("tablename"));
    }
    return tableNames;
  }
}
