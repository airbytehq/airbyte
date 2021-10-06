/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
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

package io.airbyte.test.acceptance;

import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.test.acceptance.AcceptanceTests.Type;
import java.util.HashMap;
import java.util.Map;

/**
 * This class is used to provide information related to the test databases for running the
 * {@link AcceptanceTests} on GKE. We launch 2 postgres databases in GKE as pods which act as source
 * and destination and the tests run against them. In order to allow the test instance to connect to
 * these databases we use port forwarding Refer
 * tools/bin/gke-kube-acceptance-test/acceptance_test_kube_gke.sh for more info
 */
public class GKEPostgresConfig {

  private static final String SOURCE_HOST = "postgres-source-svc";
  private static final String DESTINATION_HOST = "postgres-destination-svc";
  private static final Integer PORT = 5432;
  private static final String USERNAME = "postgresadmin";
  private static final String PASSWORD = "admin123";
  private static final String DB = "postgresdb";

  public static Map<Object, Object> dbConfig(Type connectorType, boolean hiddenPassword, boolean withSchema) {
    final Map<Object, Object> dbConfig = new HashMap<>();
    dbConfig.put("host", connectorType == Type.SOURCE ? SOURCE_HOST : DESTINATION_HOST);
    dbConfig.put("password", hiddenPassword ? "**********" : PASSWORD);

    dbConfig.put("port", PORT);
    dbConfig.put("database", DB);
    dbConfig.put("username", USERNAME);

    if (withSchema) {
      dbConfig.put("schema", "public");
    }

    return dbConfig;
  }

  public static Database getSourceDatabase() {
    return Databases.createPostgresDatabase(USERNAME, PASSWORD, "jdbc:postgresql://localhost:2000/postgresdb");
  }

  public static Database getDestinationDatabase() {
    return Databases.createPostgresDatabase(USERNAME, PASSWORD, "jdbc:postgresql://localhost:3000/postgresdb");
  }

}
