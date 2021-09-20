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

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.DatabaseConfigPersistence.ConnectorInfo;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import java.io.IOException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * Unit test for the {@link DatabaseConfigPersistence#updateConnectorDefinitions} method.
 */
public class DatabaseConfigPersistenceUpdateConnectorDefinitionsTest extends BaseDatabaseConfigPersistenceTest {

  private static final JsonNode SOURCE_GITHUB_JSON = Jsons.jsonNode(SOURCE_GITHUB);
  private static final OffsetDateTime TIMESTAMP = OffsetDateTime.now();

  @BeforeAll
  public static void setup() throws Exception {
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
    configPersistence = new DatabaseConfigPersistence(database);
  }

  @AfterAll
  public static void tearDown() throws Exception {
    database.close();
  }

  @BeforeEach
  public void resetDatabase() throws SQLException {
    database.transaction(ctx -> ctx.truncateTable("airbyte_configs").execute());
  }

  @Test
  @DisplayName("When a connector does not exist, add it")
  public void testNewConnector() throws Exception {
    assertUpdateConnectorDefinition(
        Collections.emptyList(),
        Collections.emptyList(),
        List.of(SOURCE_GITHUB),
        Collections.singletonList(SOURCE_GITHUB));
  }

  @Test
  @DisplayName("When an old connector is in use, if it has all fields, do not update it")
  public void testOldConnectorInUseWithAllFields() throws Exception {
    StandardSourceDefinition currentSource = getSource().withDockerImageTag("0.0.0");
    StandardSourceDefinition latestSource = getSource().withDockerImageTag("0.1000.0");

    assertUpdateConnectorDefinition(
        Collections.singletonList(currentSource),
        Collections.singletonList(currentSource),
        Collections.singletonList(latestSource),
        Collections.singletonList(currentSource));
  }

  @Test
  @DisplayName("When a old connector is in use, add missing fields, do not update its version")
  public void testOldConnectorInUseWithMissingFields() throws Exception {
    StandardSourceDefinition currentSource = getSource().withDockerImageTag("0.0.0").withDocumentationUrl(null).withSourceType(null);
    StandardSourceDefinition latestSource = getSource().withDockerImageTag("0.1000.0");
    StandardSourceDefinition currentSourceWithNewFields = getSource().withDockerImageTag("0.0.0");

    assertUpdateConnectorDefinition(
        Collections.singletonList(currentSource),
        Collections.singletonList(currentSource),
        Collections.singletonList(latestSource),
        Collections.singletonList(currentSourceWithNewFields));
  }

  @Test
  @DisplayName("When an unused connector has a new version, update it")
  public void testUnusedConnectorWithOldVersion() throws Exception {
    StandardSourceDefinition currentSource = getSource().withDockerImageTag("0.0.0");
    StandardSourceDefinition latestSource = getSource().withDockerImageTag("0.1000.0");

    assertUpdateConnectorDefinition(
        Collections.singletonList(currentSource),
        Collections.emptyList(),
        Collections.singletonList(latestSource),
        Collections.singletonList(latestSource));
  }

  @Test
  @DisplayName("When an unused connector has missing fields, add the missing fields, do not update its version")
  public void testUnusedConnectorWithMissingFields() throws Exception {
    StandardSourceDefinition currentSource = getSource().withDockerImageTag("0.1000.0").withDocumentationUrl(null).withSourceType(null);
    StandardSourceDefinition latestSource = getSource().withDockerImageTag("0.99.0");
    StandardSourceDefinition currentSourceWithNewFields = getSource().withDockerImageTag("0.1000.0");

    assertUpdateConnectorDefinition(
        Collections.singletonList(currentSource),
        Collections.emptyList(),
        Collections.singletonList(latestSource),
        Collections.singletonList(currentSourceWithNewFields));
  }

  /**
   * Clone a source for modification and testing.
   */
  private StandardSourceDefinition getSource() {
    return Jsons.object(Jsons.clone(SOURCE_GITHUB_JSON), StandardSourceDefinition.class);
  }

  /**
   * @param currentSources all sources currently exist in the database
   * @param currentSourcesInUse a subset of currentSources; sources currently used in data syncing
   */
  private void assertUpdateConnectorDefinition(List<StandardSourceDefinition> currentSources,
                                               List<StandardSourceDefinition> currentSourcesInUse,
                                               List<StandardSourceDefinition> latestSources,
                                               List<StandardSourceDefinition> expectedUpdatedSources)
      throws Exception {
    for (StandardSourceDefinition source : currentSources) {
      writeSource(configPersistence, source);
    }

    for (StandardSourceDefinition source : currentSourcesInUse) {
      assertTrue(currentSources.contains(source), "currentSourcesInUse must exist in currentSources");
    }

    Set<String> sourceRepositoriesInUse = currentSourcesInUse.stream()
        .map(StandardSourceDefinition::getDockerRepository)
        .collect(Collectors.toSet());
    Map<String, ConnectorInfo> currentSourceRepositoryToInfo = currentSources.stream()
        .collect(Collectors.toMap(
            StandardSourceDefinition::getDockerRepository,
            s -> new ConnectorInfo(s.getSourceDefinitionId().toString(), Jsons.jsonNode(s))));

    database.transaction(ctx -> {
      try {
        configPersistence.updateConnectorDefinitions(
            ctx,
            TIMESTAMP,
            ConfigSchema.STANDARD_SOURCE_DEFINITION,
            latestSources,
            sourceRepositoriesInUse,
            currentSourceRepositoryToInfo);
      } catch (IOException e) {
        throw new SQLException(e);
      }
      return null;
    });

    assertRecordCount(expectedUpdatedSources.size());
    for (StandardSourceDefinition source : expectedUpdatedSources) {
      assertHasSource(source);
    }
  }

}
