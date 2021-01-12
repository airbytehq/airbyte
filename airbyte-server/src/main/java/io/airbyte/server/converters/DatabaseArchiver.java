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

package io.airbyte.server.converters;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.CloseableConsumer;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.scheduler.persistence.DatabaseSchema;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.Field;
import org.jooq.JSONFormat;
import org.jooq.JSONFormat.RecordFormat;
import org.jooq.Record;
import org.jooq.Table;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabaseArchiver {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabaseArchiver.class);
  private static final String DB_FOLDER_NAME = "airbyte_db";
  private static final String BACKUP_SCHEMA = "import_backup";
  private static final String DEFAULT_SCHEMA = "public";
  private static final JSONFormat DB_JSON_FORMAT = new JSONFormat().recordFormat(RecordFormat.OBJECT);

  private final ExceptionWrappingDatabase database;
  private final Path storageRoot;
  private final JsonSchemaValidator jsonSchemaValidator;

  public DatabaseArchiver(final Database database, final Path storageRoot, final JsonSchemaValidator jsonSchemaValidator) {
    this.database = new ExceptionWrappingDatabase(database);
    this.storageRoot = storageRoot;
    this.jsonSchemaValidator = jsonSchemaValidator;
  }

  public DatabaseArchiver(final Database database, final Path storageRoot) {
    this(database, storageRoot, new JsonSchemaValidator());
  }

  /**
   * Serializes each internal Airbyte Database table into a single archive file stored in YAML.
   */
  public void writeDatabaseToArchive() throws IOException {
    List<Table<?>> tables = listTables(DEFAULT_SCHEMA);
    if (tables != null) {
      tables.forEach(table -> Exceptions.toRuntime(() -> writeTableToArchive(table)));
      LOGGER.debug("Successful export of airbyte database");
    }
  }

  private List<Table<?>> listTables(final String targetSchema) throws IOException {
    if (targetSchema != null) {
      // list tables from public schema only
      return database.query(context -> context.meta().getSchemas(targetSchema).stream()
          .flatMap(schema -> context.meta(schema).getTables().stream())
          .collect(Collectors.toList()));
    } else {
      return List.of();
    }
  }

  private void writeTableToArchive(Table<?> table) throws Exception {
    final String tableName = table.getName();
    final JsonNode schema = findTableSchema(tableName);
    if (schema != null) {
      final Path tablePath = buildTablePath(tableName);
      Files.createDirectories(tablePath.getParent());
      final BufferedWriter recordOutputWriter = new BufferedWriter(new FileWriter(tablePath.toFile()));
      final CloseableConsumer<JsonNode> recordConsumer = Yamls.listWriter(recordOutputWriter);
      try (final Stream<Record> records = database.query(ctx -> ctx.select(table.fields()).from(tableName).fetchStream())) {
        records.forEach(record -> Exceptions.toRuntime(() -> {
          final Set<String> jsonFieldNames = Arrays.stream(record.fields())
              .filter(f -> f.getDataType().getTypeName().equals("jsonb"))
              .map(Field::getName)
              .collect(Collectors.toSet());
          final JsonNode row = Jsons.deserialize(record.formatJSON(DB_JSON_FORMAT));
          // for json fields, deserialize them so they are treated as objects instead of strings. this is to
          // get around that formatJson doesn't handle deserializing them for us.
          jsonFieldNames.forEach(jsonFieldName -> ((ObjectNode) row).replace(jsonFieldName, Jsons.deserialize(row.get(jsonFieldName).asText())));
          jsonSchemaValidator.ensure(schema, row);
          recordConsumer.accept(row);
        }));
      }
      recordConsumer.close();
      LOGGER.debug(String.format("Successful export of airbyte table %s", tableName));
    } else {
      throw new IllegalArgumentException(String.format("Unable to locate schema definition for table %s", tableName));
    }
  }

  private JsonNode findTableSchema(final String tableName) {
    return DatabaseSchema.find(tableName);
  }

  private Path buildTablePath(final String tableName) {
    return storageRoot
        .resolve(DB_FOLDER_NAME)
        .resolve(String.format("%s.yaml", tableName.toLowerCase()));
  }

  /**
   * Reads a YAML configuration archive file and deserialize table into the Airbyte Database. The
   * objects will be validated against the current version of Airbyte server's JSON Schema.
   */
  public String readDatabaseFromArchive() throws IOException {
    if (storageRoot.resolve(DB_FOLDER_NAME).toFile().exists()) {
      final String tempSchema = "import_staging_" + RandomStringUtils.randomAlphanumeric(5);
      Files.walk(storageRoot.resolve(DB_FOLDER_NAME))
          .filter(f -> Files.isRegularFile(f) && f.endsWith(".yaml"))
          .forEach(table -> Exceptions.toRuntime(() -> readTableFromArchive(table, tempSchema)));
      LOGGER.debug("Successful read of airbyte database from archive");
      return tempSchema;
    } else {
      LOGGER.debug("Airbyte Database was not found in the archive");
      return null;
    }
  }

  private void readTableFromArchive(final Path tablePath, final String tempSchema) throws IOException {
    final String tableName = tablePath.getFileName().toString();
    final JsonNode schema = createTable(tempSchema, tableName);
    final Stream<JsonNode> recordStream = MoreStreams.toStream(Yamls.deserialize(IOs.readFile(tablePath)).elements())
        .peek(r -> {
          try {
            jsonSchemaValidator.ensure(schema, r);
          } catch (JsonValidationException e) {
            throw new IllegalArgumentException("Archived Data Schema does not match current Airbyte Data Schemas", e);
          }
        });
    insertRecords(schema, recordStream, tempSchema, tableName);
  }

  private JsonNode createTable(final String tempSchema, final String tableName) throws IOException {
    final JsonNode schema = findTableSchema(tableName);
    final StringBuffer queryString = new StringBuffer();
    queryString.append(String.format("CREATE TABLE IF NOT EXISTS %s.%s ( \n", tempSchema, tableName));
    // TODO convert JSON schema to SQL schema
    queryString.append(") \n");
    database.query(ctx -> ctx.execute(queryString.toString()));
    return schema;
  }

  private void insertRecords(final JsonNode schema, final Stream<JsonNode> recordStream, final String tempSchema, final String tableName) {
    final StringBuffer queryString = new StringBuffer();
    queryString.append(String.format("INSERT INTO %s.%s ( \n", tempSchema, tableName));
    // TODO convert JSON schema to list of column names
    queryString.append(") VALUES\n");
    // TODO convert JSON schema to list of column types, for example "(?, ?::jsonb, ?),";
    // TODO convert Stream of JSONNode records to PreparedStatement, see
    // SqlOperationsUtils.insertRawRecordsInSingleQuery
  }

  public boolean checkDatabase(final String tempSchema) throws IOException {
    // Add sanity checks on the database in tempSchema here
    // left empty for the moment
    LOGGER.debug("Successful test of staged airbyte database");
    return !listTables(tempSchema).isEmpty();
  }

  public void commitDatabase(final String tempSchema) throws IOException {
    final StringBuffer query = new StringBuffer();
    query.append(String.format("DROP SCHEMA IF EXISTS %s CASCADE;\n", BACKUP_SCHEMA));
    query.append(String.format("ALTER SCHEMA %s RENAME TO %s;\n", DEFAULT_SCHEMA, BACKUP_SCHEMA));
    query.append(String.format("ALTER SCHEMA %s RENAME TO %s;\n", tempSchema, DEFAULT_SCHEMA));
    database.transaction(ctx -> ctx.execute(query.toString()));
    LOGGER.debug("Successful import of airbyte database");
  }

  public void dropSchema(String tempSchema) throws IOException {
    final String query = String.format("DROP SCHEMA IF EXISTS %s CASCADE;\n", tempSchema);
    database.query(ctx -> ctx.execute(query));
  }

}
