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

package io.airbyte.integrations.source.mysql;

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

public class FilteredFileDatabaseHistory extends AbstractDatabaseHistory {

  private final FileDatabaseHistory fileDatabaseHistory;
  private static String databaseName;

  public FilteredFileDatabaseHistory() {
    this.fileDatabaseHistory = new FileDatabaseHistory();
  }

  static void setDatabaseName(String databaseName) {
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
    // this is mainly for tests
    databaseName = null;
  }

  @Override
  protected void recoverRecords(Consumer<HistoryRecord> records) {
    try {
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
