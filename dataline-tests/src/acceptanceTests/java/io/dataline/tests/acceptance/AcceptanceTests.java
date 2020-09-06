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

package io.dataline.tests.acceptance;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.dataline.api.client.DatalineApiClient;
import io.dataline.api.client.invoker.ApiClient;
import io.dataline.api.client.invoker.ApiException;
import io.dataline.api.client.model.SourceIdRequestBody;
import io.dataline.api.client.model.SourceImplementationCreate;
import io.dataline.api.client.model.SourceImplementationRead;
import io.dataline.api.client.model.SourceSpecificationRead;
import io.dataline.commons.json.Jsons;
import io.dataline.config.persistence.PersistenceConstants;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class AcceptanceTests {

  static PostgreSQLContainer PSQL_DB1;

  ApiClient baseClient = new ApiClient()
      .setScheme("http")
      .setHost("localhost")
      .setPort(8001)
      .setBasePath("/api");
  DatalineApiClient apiClient = new DatalineApiClient(baseClient);

  @BeforeAll
  public static void init() {
    PSQL_DB1 = new PostgreSQLContainer();
    PSQL_DB1.start();
  }

  @Test
  public void testCreateSourceImplementation() throws IOException, ApiException {

    UUID postgresSourceId = getPostgresSourceId();
    SourceSpecificationRead sourceSpecRead =
        apiClient.getSourceSpecificationApi().getSourceSpecification(new SourceIdRequestBody().sourceId(postgresSourceId));

    JsonNode dbConfiguration = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", PSQL_DB1.getHost())
        .put("password", PSQL_DB1.getPassword())
        .put("port", PSQL_DB1.getFirstMappedPort())
        .put("dbname", PSQL_DB1.getDatabaseName())
        .put("filter_dbs", PSQL_DB1.getDatabaseName())
        .put("user", PSQL_DB1.getUsername()).build());

    UUID defaultWorkspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;
    UUID sourceSpecificationId = sourceSpecRead.getSourceSpecificationId();

    SourceImplementationCreate sourceImplementationCreate = new SourceImplementationCreate()
        .name("rldb")
        .sourceSpecificationId(sourceSpecificationId)
        .workspaceId(defaultWorkspaceId)
        .connectionConfiguration(dbConfiguration);

    SourceImplementationRead createResponse = apiClient.getSourceImplementationApi().createSourceImplementation(sourceImplementationCreate);

    assertEquals("rldb", createResponse.getName());
    assertEquals(defaultWorkspaceId, createResponse.getWorkspaceId());
    assertEquals(sourceSpecificationId, createResponse.getSourceSpecificationId());
    assertEquals(dbConfiguration, Jsons.jsonNode(createResponse.getConnectionConfiguration()));
  }

  private UUID getPostgresSourceId() throws IOException, ApiException {
    return apiClient.getSourceApi().listSources().getSources()
        .stream()
        .filter(sourceRead -> sourceRead.getName().toLowerCase().equals("postgres"))
        .findFirst()
        .orElseThrow()
        .getSourceId();
  }

}
