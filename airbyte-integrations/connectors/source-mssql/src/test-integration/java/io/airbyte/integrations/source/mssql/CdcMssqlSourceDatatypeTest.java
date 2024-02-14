/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.ContainerModifier;

public class CdcMssqlSourceDatatypeTest extends AbstractMssqlSourceDatatypeTest {

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withCdcReplication()
        .withoutSsl()
        .build();
  }

  @Override
  protected Database setupDatabase() {
    testdb = MsSQLTestDatabase.in(BaseImage.MSSQL_2022, ContainerModifier.AGENT)
        .withCdc();
    return testdb.getDatabase();
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    super.setupEnvironment(environment);
    enableCdcOnAllTables();
  }

  private void enableCdcOnAllTables() {
    testdb.with("""
                DECLARE @TableName VARCHAR(100)
                DECLARE @TableSchema VARCHAR(100)
                DECLARE CDC_Cursor CURSOR FOR
                  SELECT * FROM (
                   SELECT Name,SCHEMA_NAME(schema_id) AS TableSchema
                   FROM   sys.objects
                   WHERE  type = 'u'
                   AND is_ms_shipped <> 1
                   ) CDC
                OPEN CDC_Cursor
                FETCH NEXT FROM CDC_Cursor INTO @TableName,@TableSchema
                WHILE @@FETCH_STATUS = 0
                 BEGIN
                   DECLARE @SQL NVARCHAR(1000)
                   DECLARE @CDC_Status TINYINT
                   SET @CDC_Status=(SELECT COUNT(*)
                     FROM   cdc.change_tables
                     WHERE  Source_object_id = OBJECT_ID(@TableSchema+'.'+@TableName))
                   --IF CDC is not enabled on Table, Enable CDC
                   IF @CDC_Status <> 1
                     BEGIN
                       SET @SQL='EXEC sys.sp_cdc_enable_table
                         @source_schema = '''+@TableSchema+''',
                         @source_name   = ''' + @TableName
                                     + ''',
                         @role_name     = null;'
                       EXEC sp_executesql @SQL
                     END
                   FETCH NEXT FROM CDC_Cursor INTO @TableName,@TableSchema
                END
                CLOSE CDC_Cursor
                DEALLOCATE CDC_Cursor""");
  }

  @Override
  public boolean testCatalog() {
    return true;
  }

}
