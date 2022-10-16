/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.spy;

import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseTestProvider;
import io.airbyte.db.instance.development.DevDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevHelper;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class StreamResetPersistenceTest extends BaseDatabaseConfigPersistenceTest {

  static StreamResetPersistence streamResetPersistence;
  private static final Logger LOGGER = LoggerFactory.getLogger(StreamResetPersistenceTest.class);

  @BeforeEach
  public void setup() throws Exception {
    dataSource = DatabaseConnectionHelper.createDataSource(container);
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
    flyway = FlywayFactory.create(dataSource, DatabaseConfigPersistenceLoadDataTest.class.getName(), ConfigsDatabaseMigrator.DB_IDENTIFIER,
        ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    database = new ConfigsDatabaseTestProvider(dslContext, flyway).create(false);
    streamResetPersistence = spy(new StreamResetPersistence(database));
    final ConfigsDatabaseMigrator configsDatabaseMigrator =
        new ConfigsDatabaseMigrator(database, flyway);
    final DevDatabaseMigrator devDatabaseMigrator = new DevDatabaseMigrator(configsDatabaseMigrator);
    MigrationDevHelper.runLastMigration(devDatabaseMigrator);
    truncateAllTables();
  }

  @AfterEach
  void tearDown() throws Exception {
    dslContext.close();
    DataSourceFactory.close(dataSource);
  }

  @Test
  void testCreateSameResetTwiceOnlyCreateItOnce() throws Exception {
    final UUID connectionId = UUID.randomUUID();
    final StreamDescriptor streamDescriptor1 = new StreamDescriptor().withName("n1").withNamespace("ns2");
    final StreamDescriptor streamDescriptor2 = new StreamDescriptor().withName("n2");

    streamResetPersistence.createStreamResets(connectionId, List.of(streamDescriptor1, streamDescriptor2));

    final List<StreamDescriptor> result = streamResetPersistence.getStreamResets(connectionId);
    LOGGER.info(String.valueOf(dslContext.selectFrom("stream_reset").fetch()));
    assertEquals(2, result.size());

    streamResetPersistence.createStreamResets(connectionId, List.of(streamDescriptor1));
    LOGGER.info(String.valueOf(dslContext.selectFrom("stream_reset").fetch()));
    assertEquals(2, streamResetPersistence.getStreamResets(connectionId).size());

    streamResetPersistence.createStreamResets(connectionId, List.of(streamDescriptor2));
    LOGGER.info(String.valueOf(dslContext.selectFrom("stream_reset").fetch()));
    assertEquals(2, streamResetPersistence.getStreamResets(connectionId).size());
  }

  @Test
  void testCreateAndGetAndDeleteStreamResets() throws Exception {
    final List<StreamDescriptor> streamResetList = new ArrayList<>();
    final StreamDescriptor streamDescriptor1 = new StreamDescriptor().withName("stream_name_1").withNamespace("stream_namespace_1");
    final StreamDescriptor streamDescriptor2 = new StreamDescriptor().withName("stream_name_2");
    streamResetList.add(streamDescriptor1);
    streamResetList.add(streamDescriptor2);
    final UUID uuid = UUID.randomUUID();
    streamResetPersistence.createStreamResets(uuid, streamResetList);

    final List<StreamDescriptor> result = streamResetPersistence.getStreamResets(uuid);
    assertEquals(2, result.size());
    assertTrue(
        result.stream().anyMatch(
            streamDescriptor -> "stream_name_1".equals(streamDescriptor.getName()) && "stream_namespace_1".equals(streamDescriptor.getNamespace())));
    assertTrue(
        result.stream().anyMatch(streamDescriptor -> "stream_name_2".equals(streamDescriptor.getName()) && streamDescriptor.getNamespace() == null));

    streamResetPersistence.createStreamResets(uuid, List.of(new StreamDescriptor().withName("stream_name_3").withNamespace("stream_namespace_2")));
    streamResetPersistence.deleteStreamResets(uuid, result);

    final List<StreamDescriptor> resultAfterDeleting = streamResetPersistence.getStreamResets(uuid);
    assertEquals(1, resultAfterDeleting.size());

    assertTrue(
        resultAfterDeleting.stream().anyMatch(
            streamDescriptor -> "stream_name_3".equals(streamDescriptor.getName()) && "stream_namespace_2".equals(streamDescriptor.getNamespace())));
  }

}
