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

package io.airbyte.db.instance;

import io.airbyte.db.Database;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Path;
import java.sql.Connection;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.jooq.meta.postgres.PostgresDatabase;
import org.jooq.tools.StringUtils;
import org.jooq.tools.jdbc.JDBCUtils;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * Custom database for jOOQ code generation. It performs the following operations:
 * <li>Run Flyway migration.</li>
 * <li>Dump the database schema.</li>
 * <li>Create a connection for jOOQ code generation.</li>
 * <p/>
 * Reference: https://github.com/sabomichal/jooq-meta-postgres-flyway
 */
public abstract class FlywayMigrationDatabase extends PostgresDatabase {

  private static final String DEFAULT_DOCKER_IMAGE = "postgres:13-alpine";

  private Connection connection;

  private final String schemaDumpFile;

  protected FlywayMigrationDatabase(String schemaDumpFile) {
    this.schemaDumpFile = schemaDumpFile;
  }

  protected abstract Database getAndInitializeDatabase(String username, String password, String connectionString) throws IOException;

  protected abstract DatabaseMigrator getDatabaseMigrator(Database database);

  @Override
  protected DSLContext create0() {
    return DSL.using(getInternalConnection(), SQLDialect.POSTGRES);
  }

  protected Connection getInternalConnection() {
    if (connection == null) {
      try {
        createInternalConnection();
      } catch (Exception e) {
        throw new RuntimeException("Failed to launch postgres container and run migration", e);
      }
    }
    return connection;
  }

  private void createInternalConnection() throws Exception {
    String dockerImage = getProperties().getProperty("dockerImage");
    if (StringUtils.isBlank(dockerImage)) {
      dockerImage = DEFAULT_DOCKER_IMAGE;
    }

    PostgreSQLContainer<?> container = new PostgreSQLContainer<>(dockerImage)
        .withDatabaseName("jooq_airbyte_configs")
        .withUsername("jooq_generator")
        .withPassword("jooq_generator");
    container.start();

    Database database = getAndInitializeDatabase(container.getUsername(), container.getPassword(), container.getJdbcUrl());
    DatabaseMigrator migrator = getDatabaseMigrator(database);

    migrator.migrate();
    dumpSchemaFile(migrator);

    connection = database.getDataSource().getConnection();
    setConnection(connection);
  }

  @Override
  public void close() {
    JDBCUtils.safeClose(connection);
    connection = null;
    super.close();
  }

  public void dumpSchemaFile(DatabaseMigrator migrator) throws IOException {
    String schema = migrator.dumpSchema();
    try (PrintWriter writer = new PrintWriter(new File(Path.of(schemaDumpFile).toUri()))) {
      writer.println(schema);
    } catch (FileNotFoundException e) {
      throw new IOException(e);
    }
  }

}
