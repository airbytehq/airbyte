/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.sql.SQLException;
import java.util.List;
import io.airbyte.integrations.base.JavaBaseConstants;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TeradataSqlOperations extends JdbcSqlOperations {
private static final Logger LOGGER = LoggerFactory.getLogger(TeradataSqlOperations.class);   
       
	public TeradataSqlOperations() {
        super(new TeradataDataAdapter());
      }

    @Override
    public void insertRecordsInternal(final JdbcDatabase database,
                                    final List<AirbyteRecordMessage> records,
                                    final String schemaName,
                                    final String tmpTableName)
      throws SQLException {
    if (records.isEmpty()) {
      return;
    }

    database.execute(connection -> {
      File tmpFile = null;
      try {
        tmpFile = Files.createTempFile(tmpTableName + "-", ".tmp").toFile();
        writeBatchToFile(tmpFile, records);
        System.out.println("tmpTableName : " + tmpTableName);
        
      } catch (final Exception e) {
        throw new RuntimeException(e);
      } finally {
        try {
          if (tmpFile != null) {
            Files.delete(tmpFile.toPath());
          }
        } catch (final IOException e) {
          throw new RuntimeException(e);
        }
      }
    });
  }


   @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
   try {
       	  database.execute(String.format("CREATE DATABASE %s AS PERM = 1e9 SKEW = 10 PERCENT;", schemaName));
   }  catch (SQLException e) {


      if(e.getMessage().contains("already exists")) {
        LOGGER.warn("Database " + schemaName + " already exists.");
      }
  }

  
  
   }

  @Override
  public void createTableIfNotExists(final JdbcDatabase database, final String schemaName, final String tableName) throws SQLException {
    database.execute(createTableQuery(database, schemaName, tableName));
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
	"CREATE SET TABLE %s.%s, FALLBACK ( \n"
	+ "%s VARCHAR(25), \n"
     	+ "%s VARCHAR(100), \n"
	+ "%s DATE \n"
	+ ");\n", 
	schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);	
  }

@Override
  public void dropTableIfExists(final JdbcDatabase database, final String schemaName, final String tableName) throws SQLException {
    database.execute(dropTableIfExistsQuery(schemaName, tableName));
  }

  private String dropTableIfExistsQuery(final String schemaName, final String tableName) {
    return String.format("DROP TABLE  %s.%s;\n", schemaName, tableName);
  }
    
}

