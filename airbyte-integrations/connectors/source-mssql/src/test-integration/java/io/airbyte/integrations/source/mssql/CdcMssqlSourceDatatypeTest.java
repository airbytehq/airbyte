/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;

public class CdcMssqlSourceDatatypeTest extends AbstractMssqlSourceDatatypeTest {

  @Override
  protected JsonNode getConfig() throws Exception {
    return testdb.integrationTestConfigBuilder()
        .withCdcReplication()
        .withoutSsl()
        .build();
  }

  @Override
  protected Database setupDatabase() throws Exception {
    testdb = MsSQLTestDatabase.in("mcr.microsoft.com/mssql/server:2022-latest", "withAgent")
        .withSnapshotIsolation()
        .withCdc();
    return testdb.getDatabase();
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    super.setupEnvironment(environment);
    enableCdcOnAllTables();
  }

  private void enableCdcOnAllTables() {
    testdb.with(""
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

  @Override
  public boolean testCatalog() {
    return true;
  }

}
