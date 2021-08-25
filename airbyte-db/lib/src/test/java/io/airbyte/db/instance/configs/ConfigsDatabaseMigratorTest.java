package io.airbyte.db.instance.configs;

import io.airbyte.db.instance.DatabaseMigrator;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

public class ConfigsDatabaseMigratorTest extends AbstractConfigsDatabaseTest {

  private static final String SCHEMA_DUMP_FILE = "src/main/resources/configs_database/schema_dump.txt";

  @Test
  public void dumpSchema() throws IOException {
    DatabaseMigrator migrator = new ConfigsDatabaseMigrator(database, ConfigsDatabaseMigratorTest.class.getSimpleName());
    migrator.migrate();
    String schema = migrator.dumpSchema();
    try (PrintWriter writer = new PrintWriter(new File(Path.of(SCHEMA_DUMP_FILE).toUri()))) {
      writer.println(schema);
    } catch (FileNotFoundException e) {
      throw new IOException(e);
    }
  }

}
