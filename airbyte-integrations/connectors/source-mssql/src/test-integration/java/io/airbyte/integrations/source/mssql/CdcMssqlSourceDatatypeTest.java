/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import java.util.Map;
import org.jooq.DSLContext;
import org.testcontainers.containers.MSSQLServerContainer;

public class CdcMssqlSourceDatatypeTest extends AbstractMssqlSourceDatatypeTest {

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    dslContext.close();
    container.close();
  }

  @Override
  protected Database setupDatabase() throws Exception {
    container = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-latest")
        .acceptLicense();
    container.addEnv("MSSQL_AGENT_ENABLED", "True"); // need this running for cdc to work
    container.start();

    final JsonNode replicationConfig = Jsons.jsonNode(Map.of(
        "method", "CDC",
        "data_to_sync", "Existing and New",
        "initial_waiting_seconds", 5,
        "snapshot_isolation", "Snapshot"));

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, DB_NAME)
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .put("replication_method", replicationConfig)
        .put("is_test", true)
        .build());

    dslContext = DSLContextFactory.create(
        container.getUsername(),
        container.getPassword(),
        container.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%s;",
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt()),
        null);
    final Database database = new Database(dslContext);

    executeQuery("CREATE DATABASE " + DB_NAME + ";");
    executeQuery("ALTER DATABASE " + DB_NAME + "\n\tSET ALLOW_SNAPSHOT_ISOLATION ON");
    executeQuery("USE " + DB_NAME + "\n" + "EXEC sys.sp_cdc_enable_db");

    return database;
  }

  private void executeQuery(final String query) {
    try (final DSLContext dslContext = DSLContextFactory.create(
        DataSourceFactory.create(
            container.getUsername(),
            container.getPassword(),
            container.getDriverClassName(),
            String.format("jdbc:sqlserver://%s:%d;",
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt())),
        null)) {
      final Database database = new Database(dslContext);
      database.query(
          ctx -> ctx
              .execute(query));
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    super.setupEnvironment(environment);
    enableCdcOnAllTables();
  }

  private void enableCdcOnAllTables() {
    executeQuery("USE " + DB_NAME + "\n"
        + "DECLARE @TableName VARCHAR(100)\n"
        + "DECLARE @TableSchema VARCHAR(100)\n"
        + "DECLARE CDC_Cursor CURSOR FOR\n"
        + "  SELECT * FROM ( \n"
        + "   SELECT Name,SCHEMA_NAME(schema_id) AS TableSchema\n"
        + "   FROM   sys.objects\n"
        + "   WHERE  type = 'u'\n"
        + "   AND is_ms_shipped <> 1\n"
        + "   ) CDC\n"
        + "OPEN CDC_Cursor\n"
        + "FETCH NEXT FROM CDC_Cursor INTO @TableName,@TableSchema\n"
        + "WHILE @@FETCH_STATUS = 0\n"
        + " BEGIN\n"
        + "   DECLARE @SQL NVARCHAR(1000)\n"
        + "   DECLARE @CDC_Status TINYINT\n"
        + "   SET @CDC_Status=(SELECT COUNT(*)\n"
        + "     FROM   cdc.change_tables\n"
        + "     WHERE  Source_object_id = OBJECT_ID(@TableSchema+'.'+@TableName))\n"
        + "   --IF CDC is not enabled on Table, Enable CDC\n"
        + "   IF @CDC_Status <> 1\n"
        + "     BEGIN\n"
        + "       SET @SQL='EXEC sys.sp_cdc_enable_table\n"
        + "         @source_schema = '''+@TableSchema+''',\n"
        + "         @source_name   = ''' + @TableName\n"
        + "                     + ''',\n"
        + "         @role_name     = null;'\n"
        + "       EXEC sp_executesql @SQL\n"
        + "     END\n"
        + "   FETCH NEXT FROM CDC_Cursor INTO @TableName,@TableSchema\n"
        + "END\n"
        + "CLOSE CDC_Cursor\n"
        + "DEALLOCATE CDC_Cursor");
  }

}
