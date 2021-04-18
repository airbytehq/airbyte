package io.airbyte.db_record_generator;

import io.airbyte.db.Databases;
import io.airbyte.integrations.destination.jdbc.DefaultSqlOperations;
import java.util.UUID;
import org.apache.commons.lang3.StringUtils;

public class RecordGenerator {
  private static String jdbcUrl = "jdbc:postgresql://localhost:2000/postgres";
  private static String user = "postgres";
  private static String password = "password";

  private static int numRecords = 1_000_000;
  private static int insertBatch = 2_000;
  private static int columnLimit = 500;
  private static String fullyQualifiedTableName = "public.large_table_agri";

  public static void main(String[] args) throws Exception {
    var sqlOps = new DefaultSqlOperations();
    var postgresDB = Databases.createJdbcDatabase(user, password, jdbcUrl, "org.postgresql.Driver");

    for (int totalInsertedRecs = 0; totalInsertedRecs < numRecords; totalInsertedRecs+=insertBatch) {
      for (int currNumInsertQuery = 0; currNumInsertQuery < insertBatch; currNumInsertQuery++) {
        var queryBuffer = new StringBuffer();
        var id = UUID.randomUUID().toString();
        var title = StringUtils.repeat('*', columnLimit);
        var did = StringUtils.repeat('*', columnLimit);
        var date_prod = StringUtils.repeat('*', columnLimit);
        var kind = StringUtils.repeat('*', columnLimit);
        var len = StringUtils.repeat('*', columnLimit);

        queryBuffer.append(String.format("INSERT INTO %s (code, title, did, date_prod, kind, len) VALUES" +
            "('%s', '%s', '%s', '%s', '%s', '%s');\n", fullyQualifiedTableName, id, title, did, date_prod, kind, len));
        sqlOps.executeTransaction(postgresDB, queryBuffer.toString());
      }
      if (totalInsertedRecs % 10000 == 0)
      System.out.println("inserted: " + totalInsertedRecs);
    }

  }

}
