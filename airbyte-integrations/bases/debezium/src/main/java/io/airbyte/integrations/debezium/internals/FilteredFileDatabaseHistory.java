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

package io.airbyte.integrations.debezium.internals;

import io.debezium.config.Configuration;
import io.debezium.relational.history.AbstractDatabaseHistory;
import io.debezium.relational.history.DatabaseHistoryException;
import io.debezium.relational.history.DatabaseHistoryListener;
import io.debezium.relational.history.FileDatabaseHistory;
import io.debezium.relational.history.HistoryRecord;
import io.debezium.relational.history.HistoryRecord.Fields;
import io.debezium.relational.history.HistoryRecordComparator;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.function.Consumer;

/**
 * MySQL Debezium connector monitors the database schema evolution over the time and stores the data
 * in a database history file. Without this file we can't fetch the records from binlog. We need to
 * save the contents of the file. Debezium by default uses
 * {@link io.debezium.relational.history.FileDatabaseHistory} class to write the schema information
 * in the file. The problem is that the Debezium tracks the schema evolution of all the tables in
 * all the databases, because of that the file content can grow. In order to make sure that debezium
 * tracks only the schema of the tables that are present in the database that Airbyte is syncing, we
 * created this class. In the method {@link #storeRecord(HistoryRecord)}, we introduced a check to
 * make sure only those records are being saved whose database name matches the database Airbyte is
 * syncing. We tell debezium to use this class by passing it as property in debezium engine. Look
 * for "database.history" property in {@link DebeziumRecordPublisher#getDebeziumProperties()}
 * Ideally {@link FilteredFileDatabaseHistory} should have extended
 * {@link io.debezium.relational.history.FileDatabaseHistory} and overridden the
 * {@link #storeRecord(HistoryRecord)} method but {@link FilteredFileDatabaseHistory} is a final
 * class and can not be inherited
 */
public class FilteredFileDatabaseHistory extends AbstractDatabaseHistory {

  private final FileDatabaseHistory fileDatabaseHistory;
  private static String databaseName;

  public FilteredFileDatabaseHistory() {
    this.fileDatabaseHistory = new FileDatabaseHistory();
  }

  /**
   * Ideally the databaseName should have been initialized in the constructor of the class. But since
   * we supply the class name to debezium and it uses reflection to construct the object of the class,
   * we can't pass in the databaseName as a parameter to the constructor. That's why we had to take
   * the static approach.
   *
   * @param databaseName Name of the database that the connector is syncing
   */
  public static void setDatabaseName(String databaseName) {
    if (FilteredFileDatabaseHistory.databaseName == null) {
      FilteredFileDatabaseHistory.databaseName = databaseName;
    } else if (!FilteredFileDatabaseHistory.databaseName.equals(databaseName)) {
      throw new RuntimeException(
          "Database name has already been set : " + FilteredFileDatabaseHistory.databaseName
              + " can't set to : " + databaseName);
    }
  }

  @Override
  public void configure(Configuration config,
                        HistoryRecordComparator comparator,
                        DatabaseHistoryListener listener,
                        boolean useCatalogBeforeSchema) {
    fileDatabaseHistory.configure(config, comparator, listener, useCatalogBeforeSchema);
  }

  @Override
  public void start() {
    fileDatabaseHistory.start();
  }

  @Override
  public void storeRecord(HistoryRecord record) throws DatabaseHistoryException {
    if (record == null) {
      return;
    }
    try {
      String dbNameInRecord = record.document().getString(Fields.DATABASE_NAME);
      if (databaseName != null && dbNameInRecord != null && !dbNameInRecord.equals(databaseName)) {
        return;
      }

      /**
       * We are using reflection because the method
       * {@link io.debezium.relational.history.FileDatabaseHistory#storeRecord(HistoryRecord)} is
       * protected and can not be accessed from here
       */
      final Method storeRecordMethod = fileDatabaseHistory.getClass()
          .getDeclaredMethod("storeRecord", record.getClass());
      storeRecordMethod.setAccessible(true);
      storeRecordMethod.invoke(fileDatabaseHistory, record);
    } catch (NoSuchMethodException | InvocationTargetException | IllegalAccessException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void stop() {
    fileDatabaseHistory.stop();
    // this is just for tests
    databaseName = null;
  }

  @Override
  protected void recoverRecords(Consumer<HistoryRecord> records) {
    try {
      /**
       * We are using reflection because the method
       * {@link io.debezium.relational.history.FileDatabaseHistory#recoverRecords(Consumer)} is protected
       * and can not be accessed from here
       */
      final Method recoverRecords = fileDatabaseHistory.getClass()
          .getDeclaredMethod("recoverRecords", Consumer.class);
      recoverRecords.setAccessible(true);
      recoverRecords.invoke(fileDatabaseHistory, records);
    } catch (NoSuchMethodException | InvocationTargetException | IllegalAccessException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public boolean storageExists() {
    return fileDatabaseHistory.storageExists();
  }

  @Override
  public void initializeStorage() {
    fileDatabaseHistory.initializeStorage();
  }

  @Override
  public boolean exists() {
    return fileDatabaseHistory.exists();
  }

  @Override
  public String toString() {
    return fileDatabaseHistory.toString();
  }

}
