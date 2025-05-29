/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import io.airbyte.commons.logging.LoggingHelper.Color;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.integrations.source.mssql.cdc.MssqlDebeziumStateUtil;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Base64;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.jooq.Record;
import org.jooq.exception.DataAccessException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MSSQLServerContainer;

public class MsSqlTestDatabaseWithBackgroundThreads extends MsSQLTestDatabase {

  private abstract class AbstractMssqlTestDatabaseBackgroundThread extends Thread {

    protected Logger LOGGER = LoggerFactory.getLogger(this.getClass());
    protected final boolean PRINT_EVERY_CALL = false;

    AbstractMssqlTestDatabaseBackgroundThread() {
      this.start();
    }

    protected volatile boolean stop = false;

    protected String formatLogLine(String logLine) {
      String retVal = this.getClass().getSimpleName() + " databaseId=" + databaseId + ", containerId=" + containerId + " - " + logLine;
      return retVal;
    }

    @SuppressWarnings("try")
    public void run() {
      try (MdcScope mdcScope = new MdcScope.Builder().setPrefixColor(Color.PURPLE_BACKGROUND).setLogPrefix(this.getClass().getSimpleName())
          .build()) {
        while (!stop) {
          try {
            Thread.sleep(100);
            innerRun();
          } catch (final Throwable t) {
            LOGGER.info(formatLogLine(
                "got exception of type " + t.getClass() + ":" + StringUtils.replace(t.getMessage() + "\n" + formatStackTrace(t), "\n", "\\n")));
          }
        }
      }
    }

    private String formatStackTrace(Throwable t) {
      boolean belowCurrentCall = false;
      List<String> stackToDisplay = new LinkedList<String>();
      for (String stackString : ExceptionUtils.getStackFrames(t)) {
        if (stackString.startsWith("\tat ")) {
          if (!belowCurrentCall && stackString.contains(AbstractMssqlTestDatabaseBackgroundThread.class.getSimpleName())) {
            belowCurrentCall = true;
          }
        } else {
          belowCurrentCall = false;
        }
        if (!belowCurrentCall) {
          stackToDisplay.add(stackString);
        }
      }
      return StringUtils.join(stackToDisplay, "\n    ");
    }

    public abstract void innerRun() throws Exception;

  }

  private class MssqlTestDatabaseBackgroundThreadAgentState extends AbstractMssqlTestDatabaseBackgroundThread {

    private String previousValue = null;

    @Override
    public void innerRun() throws Exception {
      String agentStateSql = "EXEC master.dbo.xp_servicecontrol 'QueryState', N'SQLServerAGENT';";
      final var r = query(ctx -> ctx.fetch(agentStateSql).get(0));
      String agentState = r.getValue(0).toString();
      if (PRINT_EVERY_CALL || !Objects.equals(agentState, previousValue)) {
        LOGGER.info(formatLogLine("agentState changed from {} to {}"), previousValue, agentState);
        previousValue = agentState;
      }

    }

  }

  private class MssqlTestDatabaseBackgroundThreadFnCdcGetMaxLsn extends AbstractMssqlTestDatabaseBackgroundThread {

    private String previousValue = null;

    @Override
    public void innerRun() throws Exception {
      String max_lsn;
      try {
        Object retVal = query(ctx -> ctx.fetch(MAX_LSN_QUERY)).get(0).getValue(0);
        if (retVal instanceof byte[] bytes) {
          max_lsn = new String(Base64.getEncoder().encode(bytes), StandardCharsets.UTF_8);
        } else {
          max_lsn = String.valueOf(retVal);
        }
      } catch (DataAccessException e) {
        if (e.getMessage().contains("Invalid object name 'cdc.lsn_time_mapping'")) {
          max_lsn = "DataAccessException " + e.getMessage();
        } else {
          throw e;
        }
      }
      if (PRINT_EVERY_CALL || !Objects.equals(max_lsn, previousValue)) {
        LOGGER.info(formatLogLine("sys.fn_cdc_get_max_lsn changed from {} to {}"), previousValue, max_lsn);
        previousValue = max_lsn;
      }
    }

  }

  private class MssqlTestDatabaseBackgroundThreadLsnTimeMapping extends AbstractMssqlTestDatabaseBackgroundThread {

    private String previousValue = null;
    private static final String LSN_TIME_MAPPING_QUERY = "SELECT start_lsn, tran_begin_time, tran_end_time, tran_id FROM cdc.lsn_time_mapping;";

    @Override
    public void innerRun() throws Exception {
      String results;
      try {
        results = query(ctx -> ctx.fetch(LSN_TIME_MAPPING_QUERY)).toString();
      } catch (DataAccessException e) {
        if (e.getMessage().contains("Invalid object name 'cdc.lsn_time_mapping'")) {
          results = "DataAccessException " + e.getMessage();
        } else {
          throw e;
        }
      }
      if (PRINT_EVERY_CALL || !Objects.equals(results, previousValue)) {
        LOGGER.info(formatLogLine("sys.lsn_time_mapping changed from {} to {}"), previousValue, results);
        previousValue = results;
      }
    }

  }

  private class MssqlTestDatabaseBackgroundThreadQueryJobsTable extends AbstractMssqlTestDatabaseBackgroundThread {

    private String previousValue = null;
    private int previousRowCount = -1;
    private static final String JOBS_TABLE_QUERY = "SELECT * FROM msdb.dbo.cdc_jobs";

    @Override
    public void innerRun() throws Exception {
      int resultSize = 0;
      String resultsAsString;
      try {
        List<Record> results = query(ctx -> ctx.fetch(JOBS_TABLE_QUERY));
        resultsAsString = results.toString();
        resultSize = results.size();
      } catch (DataAccessException e) {
        if (e.getMessage().contains("Invalid object name 'msdb.dbo.cdc_jobs'")) {
          resultsAsString = "DataAccessException " + e.getMessage();
        } else {
          throw e;
        }
      }
      if (PRINT_EVERY_CALL || !Objects.equals(resultsAsString, previousValue)) {
        LOGGER.info(formatLogLine("cdc.change_tables changed from {} rows\n{} to {} rows\n{}"), previousRowCount, previousValue, resultSize,
            resultsAsString);
        previousValue = resultsAsString;
        previousRowCount = resultSize;
      }
    }

  }

  private class MssqlTestDatabaseBackgroundThreadQueryChangeTables extends AbstractMssqlTestDatabaseBackgroundThread {

    private String previousValue = null;
    private int previousRowCount = -1;
    private static final String CHANGE_TABLES_QUERY = """
                                                      SELECT OBJECT_SCHEMA_NAME(source_object_id, DB_ID('%s')),
                                                      OBJECT_NAME(source_object_id, DB_ID('%s')),
                                                      capture_instance,
                                                      object_id,
                                                      start_lsn FROM cdc.change_tables""";

    @Override
    public void innerRun() throws Exception {
      int resultSize = 0;
      String resultsAsString;
      try {
        List<Record> results = query(ctx -> ctx.fetch(CHANGE_TABLES_QUERY.formatted(getDatabaseName(), getDatabaseName())));
        resultsAsString = results.toString();
        resultSize = results.size();
      } catch (DataAccessException e) {
        if (e.getMessage().contains("Invalid object name 'cdc.change_tables'")) {
          resultsAsString = "DataAccessException " + e.getMessage();
        } else {
          throw e;
        }
      }
      if (PRINT_EVERY_CALL || !Objects.equals(resultsAsString, previousValue)) {
        LOGGER.info(formatLogLine("cdc.change_tables changed from {} rows\n{} to {} rows\n{}"), previousRowCount, previousValue, resultSize,
            resultsAsString);
        previousValue = resultsAsString;
        previousRowCount = resultSize;
      }
    }

  }

  private class MssqlTestDatabaseBackgroundThreadQueryCdcTable extends AbstractMssqlTestDatabaseBackgroundThread {

    private final String schemaName;
    private final String tableName;
    private final String instanceName;
    private String previousValue = null;
    private int previousRowCount = -1;

    MssqlTestDatabaseBackgroundThreadQueryCdcTable(String schemaName, String tableName, String instanceName) {
      this.schemaName = schemaName;
      this.tableName = tableName;
      this.instanceName = instanceName;
    }

    private static final String CDC_TABLE_SELECT_QUERY_STRING = "SELECT * FROM cdc.%s_ct";

    @Override
    public void innerRun() throws Exception {
      int resultSize = 0;
      String resultsAsString;
      try {
        List<Record> results = query(ctx -> ctx.fetch(CDC_TABLE_SELECT_QUERY_STRING.formatted(instanceName)));
        resultsAsString = results.toString();
        resultSize = results.size();
      } catch (DataAccessException e) {
        if (e.getMessage().contains("Invalid object name 'cdc.%s_ct'".formatted(instanceName))) {
          resultsAsString = "DataAccessException " + e.getMessage();
        } else {
          throw e;
        }
      }
      if (PRINT_EVERY_CALL || !Objects.equals(resultsAsString, previousValue)) {
        LOGGER.info(formatLogLine("cdc table {} for {}.{} changed from {} rows\n{} to {} rows\n{}"), instanceName, schemaName, tableName,
            previousRowCount, previousValue, resultSize,
            resultsAsString);
        previousValue = resultsAsString;
        previousRowCount = resultSize;
      }
    }

  }

  private final List<AbstractMssqlTestDatabaseBackgroundThread> bgThreads = new ArrayList<>();

  MsSqlTestDatabaseWithBackgroundThreads(MSSQLServerContainer<?> container) {
    super(container);

  }

  public MsSQLTestDatabase initialized() {
    super.initialized();
    bgThreads.add(new MssqlTestDatabaseBackgroundThreadAgentState());
    bgThreads.add(new MssqlTestDatabaseBackgroundThreadFnCdcGetMaxLsn());
    bgThreads.add(new MssqlTestDatabaseBackgroundThreadLsnTimeMapping());
    bgThreads.add(new MssqlTestDatabaseBackgroundThreadQueryChangeTables());
    bgThreads.add(new MssqlTestDatabaseBackgroundThreadQueryJobsTable());
    return self();
  }

  public void close() {
    for (var bgThread : bgThreads) {
      bgThread.stop = true;
    }
    super.close();
    MssqlDebeziumStateUtil.disposeInitialState();
  }

  private final Map<String, MssqlTestDatabaseBackgroundThreadQueryCdcTable> bgThreadByInstance = new ConcurrentHashMap<>();

  @Override
  public MsSQLTestDatabase withCdcForTable(String schemaName, String tableName, String roleName, String instanceName) {
    super.withCdcForTable(schemaName, tableName, roleName, instanceName);
    MssqlTestDatabaseBackgroundThreadQueryCdcTable bgThread = new MssqlTestDatabaseBackgroundThreadQueryCdcTable(schemaName, tableName, instanceName);
    bgThreadByInstance.put(instanceName, bgThread);
    bgThreads.add(bgThread);
    return this;
  }

  @Override
  public MsSQLTestDatabase withCdcDisabledForTable(String schemaName, String tableName, String instanceName) {
    bgThreadByInstance.get(instanceName).stop = true;
    super.withCdcDisabledForTable(schemaName, tableName, instanceName);
    return this;
  }

}
