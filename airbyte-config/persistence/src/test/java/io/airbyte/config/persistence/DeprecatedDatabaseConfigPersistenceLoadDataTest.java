/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.db.instance.configs.DeprecatedConfigsDatabaseInstance;
import java.util.Collections;
import java.util.UUID;
import org.jooq.DSLContext;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

/**
 * Unit test for the {@link DeprecatedDatabaseConfigPersistence#loadData} method.
 */
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class DeprecatedDatabaseConfigPersistenceLoadDataTest extends BaseDeprecatedDatabaseConfigPersistenceTest {

  private final ConfigPersistence seedPersistence = mock(ConfigPersistence.class);

  @BeforeAll
  public static void setup() throws Exception {
    database = new DeprecatedConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
    configPersistence = spy(new DeprecatedDatabaseConfigPersistence(database));
    database.query(ctx -> ctx.execute("TRUNCATE TABLE airbyte_configs"));
  }

  @AfterAll
  public static void tearDown() throws Exception {
    database.close();
  }

  @BeforeEach
  public void resetPersistence() {
    reset(seedPersistence);
    reset(configPersistence);
  }

  @Test
  @Order(1)
  @DisplayName("When database is empty, configs should be inserted")
  public void testUpdateConfigsInNonEmptyDatabase() throws Exception {
    when(seedPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class))
        .thenReturn(Lists.newArrayList(SOURCE_GITHUB));
    when(seedPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
        .thenReturn(Lists.newArrayList(DESTINATION_S3, DESTINATION_SNOWFLAKE));

    configPersistence.loadData(seedPersistence);

    // the new destination is added
    assertRecordCount(3);
    assertHasDestination(DESTINATION_SNOWFLAKE);

    verify(configPersistence, times(1)).updateConfigsFromSeed(any(DSLContext.class), any(ConfigPersistence.class));
  }

  @Test
  @Order(2)
  @DisplayName("When a connector is in use, its definition should not be updated")
  public void testNoUpdateForUsedConnector() throws Exception {
    // the seed has a newer version of s3 destination and github source
    final StandardDestinationDefinition destinationS3V2 = Jsons.clone(DESTINATION_S3).withDockerImageTag("10000.1.0");
    when(seedPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
        .thenReturn(Collections.singletonList(destinationS3V2));
    final StandardSourceDefinition sourceGithubV2 = Jsons.clone(SOURCE_GITHUB).withDockerImageTag("10000.15.3");
    when(seedPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class))
        .thenReturn(Collections.singletonList(sourceGithubV2));

    // create connections to mark the source and destination as in use
    final DestinationConnection s3Connection = new DestinationConnection()
        .withDestinationId(UUID.randomUUID())
        .withDestinationDefinitionId(destinationS3V2.getDestinationDefinitionId());
    configPersistence.writeConfig(ConfigSchema.DESTINATION_CONNECTION, s3Connection.getDestinationId().toString(), s3Connection);
    final SourceConnection githubConnection = new SourceConnection()
        .withSourceId(UUID.randomUUID())
        .withSourceDefinitionId(sourceGithubV2.getSourceDefinitionId());
    configPersistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, githubConnection.getSourceId().toString(), githubConnection);

    configPersistence.loadData(seedPersistence);
    // s3 destination is not updated
    assertHasDestination(DESTINATION_S3);
    assertHasSource(SOURCE_GITHUB);
  }

  @Test
  @Order(3)
  @DisplayName("When a connector is not in use, its definition should be updated")
  public void testUpdateForUnusedConnector() throws Exception {
    // the seed has a newer version of snowflake destination
    final StandardDestinationDefinition snowflakeV2 = Jsons.clone(DESTINATION_SNOWFLAKE).withDockerImageTag("10000.2.0");
    when(seedPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
        .thenReturn(Collections.singletonList(snowflakeV2));

    configPersistence.loadData(seedPersistence);
    assertHasDestination(snowflakeV2);
  }

}
