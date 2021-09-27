/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.migration;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import java.io.IOException;
import org.testcontainers.containers.PostgreSQLContainer;

public class StubAirbyteDB implements AutoCloseable {

  private final PostgreSQLContainer<?> container;
  private final Database database;

  public Database getDatabase() {
    return database;
  }

  public StubAirbyteDB() throws IOException {
    container =
        new PostgreSQLContainer<>("postgres:13-alpine")
            .withDatabaseName("airbyte")
            .withUsername("docker")
            .withPassword("docker");
    container.start();

    String jobsDatabaseSchema = MoreResources.readResource("migration/schema.sql");
    database = new JobsDatabaseInstance(
        container.getUsername(),
        container.getPassword(),
        container.getJdbcUrl(),
        jobsDatabaseSchema)
            .getAndInitialize();
  }

  @Override
  public void close() throws Exception {
    database.close();
    container.close();
  }

}
