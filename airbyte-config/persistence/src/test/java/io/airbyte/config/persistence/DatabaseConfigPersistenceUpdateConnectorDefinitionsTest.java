/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
    final StandardSourceDefinition currentSource = getSource().withDockerImageTag("0.0.0");
    final StandardSourceDefinition latestSource = getSource().withDockerImageTag("0.1000.0");

    assertUpdateConnectorDefinition(
        Collections.singletonList(currentSource),
        Collections.singletonList(currentSource),
        Collections.singletonList(latestSource),
        Collections.singletonList(currentSource));
  }

  @Test
  @DisplayName("When a old connector is in use, add missing fields, do not update its version")
  public void testOldConnectorInUseWithMissingFields() throws Exception {
    final StandardSourceDefinition currentSource = getSource().withDockerImageTag("0.0.0").withDocumentationUrl(null).withSourceType(null);
    final StandardSourceDefinition latestSource = getSource().withDockerImageTag("0.1000.0");
    final StandardSourceDefinition currentSourceWithNewFields = getSource().withDockerImageTag("0.0.0");

    assertUpdateConnectorDefinition(
        Collections.singletonList(currentSource),
        Collections.singletonList(currentSource),
        Collections.singletonList(latestSource),
        Collections.singletonList(currentSourceWithNewFields));
  }

  @Test
  @DisplayName("When an unused connector has a new version, update it")
  public void testUnusedConnectorWithOldVersion() throws Exception {
    final StandardSourceDefinition currentSource = getSource().withDockerImageTag("0.0.0");
    final StandardSourceDefinition latestSource = getSource().withDockerImageTag("0.1000.0");

    assertUpdateConnectorDefinition(
        Collections.singletonList(currentSource),
        Collections.emptyList(),
        Collections.singletonList(latestSource),
        Collections.singletonList(latestSource));
  }

  @Test
  @DisplayName("When an unused connector has missing fields, add the missing fields, do not update its version")
  public void testUnusedConnectorWithMissingFields() throws Exception {
    final StandardSourceDefinition currentSource = getSource().withDockerImageTag("0.1000.0").withDocumentationUrl(null).withSourceType(null);
    final StandardSourceDefinition latestSource = getSource().withDockerImageTag("0.99.0");
    final StandardSourceDefinition currentSourceWithNewFields = getSource().withDockerImageTag("0.1000.0");

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
  private void assertUpdateConnectorDefinition(final List<StandardSourceDefinition> currentSources,
                                               final List<StandardSourceDefinition> currentSourcesInUse,
                                               final List<StandardSourceDefinition> latestSources,
                                               final List<StandardSourceDefinition> expectedUpdatedSources)
      throws Exception {
    for (final StandardSourceDefinition source : currentSources) {
      writeSource(configPersistence, source);
    }

    for (final StandardSourceDefinition source : currentSourcesInUse) {
      assertTrue(currentSources.contains(source), "currentSourcesInUse must exist in currentSources");
    }

    final Set<String> sourceRepositoriesInUse = currentSourcesInUse.stream()
        .map(StandardSourceDefinition::getDockerRepository)
        .collect(Collectors.toSet());
    final Map<String, ConnectorInfo> currentSourceRepositoryToInfo = currentSources.stream()
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
      } catch (final IOException e) {
        throw new SQLException(e);
      }
      return null;
    });

    assertRecordCount(expectedUpdatedSources.size());
    for (final StandardSourceDefinition source : expectedUpdatedSources) {
      assertHasSource(source);
    }
  }

}
