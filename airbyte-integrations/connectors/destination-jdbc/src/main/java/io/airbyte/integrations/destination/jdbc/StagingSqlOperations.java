package io.airbyte.integrations.destination.jdbc;

import io.airbyte.db.jdbc.JdbcDatabase;

public interface StagingSqlOperations extends SqlOperations {

  void createStageIfNotExists(JdbcDatabase database, String stage) throws Exception;

  void copyIntoTmpTableFromStage(JdbcDatabase database, String path, String srcTableName, String schemaName) throws Exception;

  void cleanUpStage(JdbcDatabase database, String path) throws Exception;

  void dropStageIfExists(JdbcDatabase database, String stageName) throws Exception;
}
